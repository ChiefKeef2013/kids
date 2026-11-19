from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import BookingForm, ContactForm, LoginForm, NewsletterForm, RegisterForm
from .models import (
    Club,
    Group,
    MasterClass,
    Payment,
    PricePlan,
    Review,
    Schedule,
    Subscription,
    Teacher,
)

AGE_BUCKETS = {
    "3-5": (3, 5),
    "6-8": (6, 8),
    "9-11": (9, 11),
    "12-14": (12, 14),
}

DIRECTIONS = [
    ("tech", "Техническое"),
    ("art", "Художественное"),
    ("lang", "Языковое"),
    ("dev", "Развивающее"),
]


def _next_saturday():
    today = date.today()
    delta = (5 - today.weekday()) % 7
    return today + timedelta(days=delta)


def _text_matches(obj, query, *fields):
    """Регистронезависимый поиск с кириллицей (SQLite не умеет unicode LIKE)."""
    needle = query.lower()
    for field in fields:
        if needle in str(getattr(obj, field) or "").lower():
            return True
    return False


def home(request):
    clubs = list(Club.objects.all())
    preview_day = _next_saturday()
    day_schedule = (
        Schedule.objects.filter(day_of_week=preview_day.isoweekday())
        .select_related("group__club", "room")
        .prefetch_related("group__teachers")[:3]
    )
    events = MasterClass.objects.filter(date__gte=date.today()).select_related("teacher", "room")
    next_event = events.first()
    groups_total = Group.objects.count()
    teachers_total = Teacher.objects.count()
    categories = len({c.direction for c in clubs})
    context = {
        "clubs": clubs,
        "preview_day": preview_day,
        "day_schedule": day_schedule,
        "next_event": next_event,
        "teachers": Teacher.objects.all()[:3],
        "reviews": Review.objects.filter(is_published=True)[:2],
        "stats": {
            "clubs": len(clubs),
            "groups": groups_total,
            "teachers": teachers_total,
            "directions": categories,
        },
    }
    return render(request, "kids/home.html", context)


def clubs(request):
    queryset = Club.objects.all()

    age = request.GET.get("age", "")
    direction = request.GET.get("direction", "")
    search = request.GET.get("search", "").strip()
    sort = request.GET.get("sort", "order")

    if age in AGE_BUCKETS:
        low, high = AGE_BUCKETS[age]
        queryset = queryset.filter(age_min__lte=high, age_max__gte=low)
    if direction in dict(DIRECTIONS):
        queryset = queryset.filter(direction=direction)

    items = list(queryset)
    if search:
        items = [club for club in items if _text_matches(club, search, "name", "tagline")]
    if sort == "price":
        items.sort(key=lambda club: club.price)
    elif sort == "age":
        items.sort(key=lambda club: club.age_min)
    else:
        items.sort(key=lambda club: (club.order, club.name))

    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    groups_total = Group.objects.filter(club__in=items).count()

    context = {
        "page_obj": page_obj,
        "age": age,
        "direction": direction,
        "search": search,
        "sort": sort,
        "directions": DIRECTIONS,
        "active_filters": sum(bool(v) for v in (age, direction, search)),
        "groups_total": groups_total,
        "is_filtered": bool(age or direction or search),
    }
    if request.headers.get("x-requested-with") == "fetch":
        context["html"] = render_to_string("kids/partials/club_cards.html", context, request=request)
        context["total"] = paginator.count
        context["groups_total"] = groups_total
        context["page"] = page_obj.number
        context["pages"] = paginator.num_pages
        return JsonResponse({k: v for k, v in context.items() if k in ("html", "total", "groups_total", "page", "pages")})
    return render(request, "kids/clubs.html", context)


def club_detail(request, slug):
    club = get_object_or_404(Club, slug=slug)
    groups = (
        club.groups.select_related("room")
        .prefetch_related(Prefetch("schedules", queryset=Schedule.objects.select_related("room")))
        .prefetch_related("teachers")
    )
    similar = Club.objects.exclude(pk=club.pk)[:3]
    context = {"club": club, "groups": groups, "similar": similar}
    return render(request, "kids/club_detail.html", context)


def schedule(request):
    queryset = Schedule.objects.select_related("group__club", "room").prefetch_related("group__teachers")
    direction = request.GET.get("direction", "")
    day = request.GET.get("day", "")
    if direction in dict(DIRECTIONS):
        queryset = queryset.filter(group__club__direction=direction)
    if day.isdigit():
        queryset = queryset.filter(day_of_week=int(day))

    days = []
    for value, label in Schedule.DAY_CHOICES:
        items = [item for item in queryset if item.day_of_week == value]
        if items:
            days.append({"value": value, "label": label, "items": items})

    context = {
        "days": days,
        "direction": direction,
        "day": day,
        "directions": DIRECTIONS,
        "day_choices": Schedule.DAY_CHOICES,
        "total": len(queryset),
        "events": MasterClass.objects.filter(date__gte=date.today())[:3],
    }
    return render(request, "kids/schedule.html", context)


def master_classes(request):
    events = MasterClass.objects.select_related("teacher", "room")
    period = request.GET.get("period", "")
    if period == "weekend":
        events = events.filter(date__week_day__in=(1, 7))
    elif period == "weekday":
        events = events.exclude(date__week_day__in=(1, 7))
    context = {"events": events, "period": period}
    return render(request, "kids/master_classes.html", context)


def teachers(request):
    context = {"teachers": Teacher.objects.prefetch_related("groups__club")}
    return render(request, "kids/teachers.html", context)


def pricing(request):
    context = {"plans": PricePlan.objects.all()}
    return render(request, "kids/pricing.html", context)


def about(request):
    context = {
        "reviews": Review.objects.filter(is_published=True),
        "stats": {
            "clubs": Club.objects.count(),
            "groups": Group.objects.count(),
            "teachers": Teacher.objects.count(),
        },
    }
    return render(request, "kids/about.html", context)


def contacts(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Сообщение отправлено — ответим в течение рабочего дня.")
        return redirect("contacts")
    return render(request, "kids/contacts.html", {"form": form})


def booking(request):
    initial = {}
    slug = request.GET.get("club")
    if slug:
        club = Club.objects.filter(slug=slug).first()
        if club:
            initial["club"] = club
    form = BookingForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Заявка отправлена. Администратор перезвонит в течение рабочего дня и подтвердит место.",
        )
        return redirect("booking")
    featured = initial.get("club")
    if not featured and request.method == "POST":
        featured = Club.objects.filter(pk=request.POST.get("club") or 0).first()
    return render(request, "kids/booking.html", {"form": form, "featured": featured})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("account")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Вы вошли в личный кабинет.")
            return redirect(request.GET.get("next") or "account")
        messages.error(request, "Неверный e-mail или пароль")
    return render(request, "kids/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Вы вышли из кабинета.")
    return redirect("home")


def register(request):
    if request.user.is_authenticated:
        return redirect("account")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Аккаунт создан. Добавьте ребёнка и запишитесь на занятие.")
        return redirect("account")
    return render(request, "kids/register.html", {"form": form})


@login_required
def account(request):
    children = list(request.user.children.all())
    subscriptions = (
        Subscription.objects.filter(child__parent=request.user)
        .select_related("child", "group__club", "group__room")
        .prefetch_related("group__teachers")
    )
    attendance = (
        request.user.children.all()
        .values("full_name", "attendance__date", "attendance__status", "attendance__schedule__group__club__name")
        .order_by("-attendance__date")[:8]
    )
    payments = Payment.objects.filter(child__parent=request.user)[:6]
    next_lessons = (
        Schedule.objects.filter(group__subscriptions__child__parent=request.user, group__subscriptions__status="active")
        .select_related("group__club", "room")
        .distinct()
        .order_by("day_of_week", "start_time")[:4]
    )
    context = {
        "children": children,
        "subscriptions": subscriptions,
        "attendance": attendance,
        "payments": payments,
        "next_lessons": next_lessons,
    }
    return render(request, "kids/account.html", context)


def search(request):
    query = request.GET.get("q", "").strip()
    clubs_found = teachers_found = events_found = []
    if query:
        clubs_found = [club for club in Club.objects.all() if _text_matches(club, query, "name", "tagline")]
        teachers_found = [
            teacher
            for teacher in Teacher.objects.all()
            if _text_matches(teacher, query, "full_name", "specialization")
        ]
        events_found = [
            event for event in MasterClass.objects.all() if _text_matches(event, query, "title", "summary")
        ]
    total = len(clubs_found) + len(teachers_found) + len(events_found)
    context = {
        "query": query,
        "clubs": clubs_found,
        "teachers": teachers_found,
        "events": events_found,
        "total": total,
    }
    return render(request, "kids/search.html", context)


def api_clubs(request):
    """JSON для фильтра каталога без перезагрузки страницы."""
    queryset = Club.objects.all()
    age = request.GET.get("age", "")
    direction = request.GET.get("direction", "")
    search = request.GET.get("search", "").strip()
    page_number = request.GET.get("page")

    if age in AGE_BUCKETS:
        low, high = AGE_BUCKETS[age]
        queryset = queryset.filter(age_min__lte=high, age_max__gte=low)
    if direction in dict(DIRECTIONS):
        queryset = queryset.filter(direction=direction)

    items = list(queryset)
    if search:
        items = [club for club in items if _text_matches(club, search, "name", "tagline")]

    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(page_number)
    html = render_to_string(
        "kids/partials/club_cards.html",
        {"page_obj": page_obj, "is_filtered": bool(age or direction or search)},
        request=request,
    )
    return JsonResponse(
        {
            "html": html,
            "total": paginator.count,
            "groups_total": Group.objects.filter(club__in=items).count(),
            "page": page_obj.number,
            "pages": paginator.num_pages,
        }
    )


def api_suggest(request):
    """Живой поиск: подсказки по направлениям, педагогам и мастер-классам."""
    query = request.GET.get("q", "").strip()
    items = []
    if len(query) >= 2:
        for club in Club.objects.all():
            if _text_matches(club, query, "name", "tagline"):
                items.append({"title": club.name, "type": "Направление", "url": club.get_absolute_url()})
        for teacher in Teacher.objects.all():
            if _text_matches(teacher, query, "full_name", "specialization"):
                items.append({"title": teacher.full_name, "type": "Педагог", "url": reverse("teachers")})
        for event in MasterClass.objects.all():
            if _text_matches(event, query, "title", "summary"):
                items.append({"title": event.title, "type": "Мастер-класс", "url": reverse("master_classes")})
        items = items[:8]
    return JsonResponse({"items": items, "query": query})


@require_POST
def newsletter(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"].lower()
        if form.Meta.model.objects.filter(email=email).exists():
            messages.info(request, "Этот адрес уже подписан на новости центра.")
        else:
            form.save()
            messages.success(request, "Готово: письма о мастер-классах будут приходить раз в две недели.")
    else:
        messages.error(request, "Проверьте адрес электронной почты")
    return redirect(request.META.get("HTTP_REFERER") or "home")


def handler404(request, exception):
    return render(request, "kids/404.html", status=404)

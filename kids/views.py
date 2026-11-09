from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg
from django.core.paginator import Paginator
from datetime import date, timedelta
import csv
from .models import Child, Club, Teacher, Group, Room, Schedule, Subscription, Attendance, MedicalCertificate

def home(request):
    return render(request, 'kids/home.html')

def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    children = Child.objects.filter(parent=request.user) if request.user.is_authenticated else []
    return render(request, 'kids/group_detail.html', {'group': group, 'children': children})

@login_required
def enroll_child(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    child_id = request.POST.get('child_id')
    child = get_object_or_404(Child, id=child_id, parent=request.user)
    
    age = child.get_age()
    
    if age < group.min_age or age > group.max_age:
        messages.error(request, f"Возраст ребёнка ({age} лет) не подходит для этой группы ({group.min_age}-{group.max_age} лет).")
        return redirect('catalog')
    
    with transaction.atomic():
        Subscription.objects.create(
            child=child,
            group=group,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            remaining_classes=8,
            status='active'
        )
    
    messages.success(request, "Ребёнок успешно записан в группу!")
    return redirect('dashboard')

def check_group_capacity(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    current_subscriptions = Subscription.objects.filter(group=group, status='active').count()
    available = group.capacity - current_subscriptions
    return JsonResponse({'available': available, 'capacity': group.capacity})

def catalog(request):
    groups = Group.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        groups = groups.filter(club__name__icontains=search)
        
    min_age = request.GET.get('min_age')
    if min_age:
        groups = groups.filter(min_age__lte=min_age)
        
    direction = request.GET.get('direction')
    if direction:
        groups = groups.filter(club__direction__icontains=direction)
        
    day = request.GET.get('day')
    if day:
        groups = groups.filter(schedules__day_of_week=day)
        
    sort = request.GET.get('sort', 'name')
    if sort == 'age':
        groups = groups.order_by('min_age')
    else:
        groups = groups.order_by('club__name')
        
    paginator = Paginator(groups, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'kids/catalog.html', {'page_obj': page_obj})

@login_required
def dashboard(request):
    total_children = Child.objects.filter(parent=request.user).count()
    active_subscriptions = Subscription.objects.filter(child__parent=request.user, status='active').count()
    avg_classes = Subscription.objects.filter(child__parent=request.user).aggregate(Avg('remaining_classes'))['remaining_classes__avg'] or 0
    total_groups = Group.objects.count()
    
    children = Child.objects.filter(parent=request.user)
    
    return render(request, 'kids/dashboard.html', {
        'total_children': total_children,
        'active_subscriptions': active_subscriptions,
        'avg_classes': round(avg_classes, 1),
        'total_groups': total_groups,
        'children': children
    })

@login_required
def upload_certificate(request, subscription_id):
    subscription = get_object_or_404(Subscription, id=subscription_id, child__parent=request.user)
    
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        if file.size > 5 * 1024 * 1024:
            messages.error(request, 'Файл слишком большой (максимум 5 МБ).')
            return redirect('dashboard')
            
        if not file.name.lower().endswith(('.pdf', '.jpg', '.jpeg')):
            messages.error(request, 'Разрешены только PDF и JPG файлы.')
            return redirect('dashboard')
        
        MedicalCertificate.objects.create(
            subscription=subscription,
            file=file,
            status='pending'
        )
        messages.success(request, 'Справка загружена и отправлена на проверку.')
        return redirect('dashboard')
    
    return render(request, 'kids/upload_certificate.html', {'subscription': subscription})

def export_attendance(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Ребёнок', 'Дата', 'Статус'])
    
    for record in Attendance.objects.all()[:50]:
        writer.writerow([record.child.full_name, record.date, record.status])
        
    return response
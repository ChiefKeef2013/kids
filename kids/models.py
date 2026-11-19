from datetime import date, timedelta

from django.contrib.auth.models import User
from django.db import models


class Club(models.Model):
    """Направление (кружок) центра."""

    COVER_CHOICES = [
        ("robo", "Робототехника"),
        ("art", "Рисование"),
        ("en", "Английский"),
        ("school", "Подготовка к школе"),
        ("science", "Наука"),
        ("theatre", "Театр"),
        ("chess", "Шахматы"),
        ("music", "Музыка"),
    ]
    DIRECTION_CHOICES = [
        ("tech", "Техническое"),
        ("art", "Художественное"),
        ("lang", "Языковое"),
        ("dev", "Развивающее"),
    ]

    name = models.CharField("название", max_length=120)
    slug = models.SlugField("адрес", max_length=120, unique=True, allow_unicode=True)
    direction = models.CharField("направление", max_length=10, choices=DIRECTION_CHOICES)
    age_min = models.PositiveSmallIntegerField("возраст от")
    age_max = models.PositiveSmallIntegerField("возраст до")
    tagline = models.CharField("короткое описание", max_length=200)
    description = models.TextField("о программе")
    skills = models.TextField("чему научится", help_text="Каждый пункт с новой строки")
    format_text = models.TextField("как проходит занятие")
    price = models.PositiveIntegerField("цена за месяц, ₽")
    lessons_per_week = models.PositiveSmallIntegerField("занятий в неделю", default=2)
    cover = models.CharField("обложка", max_length=10, choices=COVER_CHOICES)
    order = models.PositiveSmallIntegerField("порядок", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "направление"
        verbose_name_plural = "направления"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("club", kwargs={"slug": self.slug})

    @property
    def age_range(self):
        return f"{self.age_min}–{self.age_max} лет"

    @property
    def skills_list(self):
        return [line.strip() for line in self.skills.splitlines() if line.strip()]

    @property
    def groups_count(self):
        return self.groups.count()

    @property
    def students_count(self):
        return Subscription.objects.filter(group__club=self, status="active").count()

    @property
    def free_places(self):
        total = sum(g.capacity for g in self.groups.all())
        return max(total - self.students_count, 0)

    @property
    def places_tag(self):
        """Статус для карточки каталога."""
        free = self.free_places
        if free == 0:
            return ("", "Набор закрыт")
        if free <= 3:
            return ("tag--accent", f"Осталось {free}")
        return ("tag--sage", "Есть места")

    @property
    def cover_class(self):
        return f"cover--{self.cover}"


class Teacher(models.Model):
    TONE_CHOICES = [
        ("plain", "Нейтральный"),
        ("accent", "Тёплый"),
        ("sage", "Зелёный"),
    ]

    full_name = models.CharField("ФИО", max_length=150)
    specialization = models.CharField("специализация", max_length=150)
    bio = models.TextField("о педагоге")
    experience_years = models.PositiveSmallIntegerField("опыт, лет", default=3)
    tone = models.CharField("цвет карточки", max_length=10, choices=TONE_CHOICES, default="plain")
    order = models.PositiveSmallIntegerField("порядок", default=0)

    class Meta:
        ordering = ["order", "full_name"]
        verbose_name = "педагог"
        verbose_name_plural = "педагоги"

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        parts = self.full_name.split()
        return "".join(p[0] for p in parts[:2]).upper()

    @property
    def tone_class(self):
        return "" if self.tone == "plain" else f"teacher-photo--{self.tone}"


class Room(models.Model):
    number = models.CharField("номер", max_length=20)
    capacity = models.PositiveSmallIntegerField("вместимость")

    class Meta:
        ordering = ["number"]
        verbose_name = "кабинет"
        verbose_name_plural = "кабинеты"

    def __str__(self):
        return f"каб. {self.number}"


class Group(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="groups", verbose_name="направление")
    title = models.CharField("название группы", max_length=80)
    teachers = models.ManyToManyField(Teacher, related_name="groups", verbose_name="педагоги", blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, verbose_name="кабинет")
    min_age = models.PositiveSmallIntegerField("возраст от")
    max_age = models.PositiveSmallIntegerField("возраст до")
    capacity = models.PositiveSmallIntegerField("мест в группе")

    class Meta:
        ordering = ["club__order", "title"]
        verbose_name = "группа"
        verbose_name_plural = "группы"

    def __str__(self):
        return f"{self.club.name} · {self.title}"

    @property
    def age_range(self):
        return f"{self.min_age}–{self.max_age}"

    @property
    def taken_places(self):
        return self.subscriptions.filter(status="active").count()

    @property
    def free_places(self):
        return max(self.capacity - self.taken_places, 0)

    @property
    def places_status(self):
        free = self.free_places
        if free == 0:
            return "wait", "Лист ожидания"
        if free <= 2:
            return "few", f"Осталось {free}"
        return "free", "Есть места"

    @property
    def teacher(self):
        return self.teachers.first()


class Schedule(models.Model):
    DAY_CHOICES = [
        (1, "Понедельник"),
        (2, "Вторник"),
        (3, "Среда"),
        (4, "Четверг"),
        (5, "Пятница"),
        (6, "Суббота"),
    ]
    DAY_SHORT = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб"}

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="schedules", verbose_name="группа")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, verbose_name="кабинет")
    day_of_week = models.IntegerField("день недели", choices=DAY_CHOICES)
    start_time = models.TimeField("начало")
    end_time = models.TimeField("конец")

    class Meta:
        ordering = ["day_of_week", "start_time"]
        verbose_name = "занятие в расписании"
        verbose_name_plural = "расписание"

    def __str__(self):
        return f"{self.group} · {self.day_name} {self.start_time:%H:%M}"

    @property
    def day_name(self):
        return self.get_day_of_week_display()

    @property
    def day_short(self):
        return self.DAY_SHORT.get(self.day_of_week, "")

    @property
    def time_range(self):
        return f"{self.start_time:%H:%M}–{self.end_time:%H:%M}"


class MasterClass(models.Model):
    title = models.CharField("название", max_length=150)
    slug = models.SlugField("адрес", max_length=150, unique=True, allow_unicode=True)
    date = models.DateField("дата")
    start_time = models.TimeField("начало")
    end_time = models.TimeField("конец")
    age_min = models.PositiveSmallIntegerField("возраст от")
    age_max = models.PositiveSmallIntegerField("возраст до")
    price = models.PositiveIntegerField("цена, ₽")
    seats = models.PositiveSmallIntegerField("всего мест")
    seats_taken = models.PositiveSmallIntegerField("занято мест", default=0)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name="ведущий")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, verbose_name="кабинет")
    summary = models.CharField("короткое описание", max_length=250)
    program = models.TextField("программа")
    cover = models.CharField("обложка", max_length=10, choices=Club.COVER_CHOICES, default="robo")

    class Meta:
        ordering = ["date", "start_time"]
        verbose_name = "мастер-класс"
        verbose_name_plural = "мастер-классы"

    def __str__(self):
        return self.title

    @property
    def free_seats(self):
        return max(self.seats - self.seats_taken, 0)

    @property
    def is_open(self):
        return self.free_seats > 0 and self.date >= date.today()

    @property
    def age_range(self):
        return f"{self.age_min}–{self.age_max} лет"

    @property
    def time_range(self):
        return f"{self.start_time:%H:%M}–{self.end_time:%H:%M}"

    @property
    def cover_class(self):
        return f"cover--{self.cover}"


class PricePlan(models.Model):
    name = models.CharField("название", max_length=80)
    price = models.PositiveIntegerField("цена, ₽")
    lessons = models.PositiveSmallIntegerField("занятий в месяц")
    description = models.CharField("пояснение", max_length=200)
    features = models.TextField("что входит", help_text="Каждый пункт с новой строки")
    is_featured = models.BooleanField("выделить", default=False)
    order = models.PositiveSmallIntegerField("порядок", default=0)

    class Meta:
        ordering = ["order", "price"]
        verbose_name = "абонемент"
        verbose_name_plural = "абонементы"

    def __str__(self):
        return self.name

    @property
    def features_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class Review(models.Model):
    author = models.CharField("автор", max_length=100)
    child = models.CharField("ребёнок", max_length=120)
    club = models.CharField("направление", max_length=120)
    months = models.PositiveSmallIntegerField("месяцев занятий")
    text = models.TextField("текст")
    is_published = models.BooleanField("опубликован", default=True)
    order = models.PositiveSmallIntegerField("порядок", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    def __str__(self):
        return f"{self.author} · {self.club}"


class BookingRequest(models.Model):
    AGE_CHOICES = [(age, f"{age} лет") for age in range(3, 15)]
    DAY_CHOICES = [
        ("", "Любой день"),
        ("weekday", "Будни"),
        ("sat", "Суббота"),
    ]
    TIME_CHOICES = [
        ("", "Любое время"),
        ("morning", "Утро, до 12:00"),
        ("day", "День, 12:00–17:00"),
        ("evening", "Вечер, после 17:00"),
    ]

    parent_name = models.CharField("имя родителя", max_length=60)
    phone = models.CharField("телефон", max_length=20)
    email = models.EmailField("e-mail", blank=True)
    child_name = models.CharField("имя ребёнка", max_length=40)
    child_age = models.PositiveSmallIntegerField("возраст ребёнка", choices=AGE_CHOICES)
    club = models.ForeignKey(Club, on_delete=models.PROTECT, related_name="requests", verbose_name="направление")
    preferred_day = models.CharField("удобный день", max_length=10, choices=DAY_CHOICES, blank=True)
    preferred_time = models.CharField("удобное время", max_length=10, choices=TIME_CHOICES, blank=True)
    comment = models.TextField("комментарий", max_length=500, blank=True)
    consent = models.BooleanField("согласие на обработку данных")
    created_at = models.DateTimeField("создана", auto_now_add=True)
    is_processed = models.BooleanField("обработана", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "заявка на пробное занятие"
        verbose_name_plural = "заявки на пробное занятие"

    def __str__(self):
        return f"{self.parent_name} · {self.child_name} · {self.club}"


class ContactRequest(models.Model):
    TOPIC_CHOICES = [
        ("booking", "Запись и расписание"),
        ("payment", "Оплата и абонементы"),
        ("docs", "Справки и документы"),
        ("other", "Другое"),
    ]

    name = models.CharField("имя", max_length=40)
    phone = models.CharField("телефон", max_length=20)
    topic = models.CharField("тема", max_length=10, choices=TOPIC_CHOICES, blank=True)
    message = models.TextField("сообщение", max_length=1000)
    consent = models.BooleanField("согласие на обработку данных")
    created_at = models.DateTimeField("создано", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "обращение"
        verbose_name_plural = "обращения"

    def __str__(self):
        return f"{self.name} · {self.get_topic_display()}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField("e-mail", unique=True)
    created_at = models.DateTimeField("подписан", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "подписчик"
        verbose_name_plural = "подписчики"

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="пользователь")
    phone = models.CharField("телефон", max_length=20, blank=True)

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Child(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="children", verbose_name="родитель")
    full_name = models.CharField("ФИО", max_length=200)
    birth_date = models.DateField("дата рождения")

    class Meta:
        ordering = ["full_name"]
        verbose_name = "ребёнок"
        verbose_name_plural = "дети"

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def short_name(self):
        return self.full_name.split()[0]

    @property
    def initial(self):
        return self.full_name[0].upper()


class Subscription(models.Model):
    STATUS_CHOICES = [("active", "Активен"), ("expired", "Истёк")]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="ребёнок")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="группа")
    start_date = models.DateField("начало")
    end_date = models.DateField("конец")
    total_classes = models.PositiveSmallIntegerField("занятий в абонементе", default=8)
    remaining_classes = models.IntegerField("осталось занятий", default=0)
    status = models.CharField("статус", max_length=20, choices=STATUS_CHOICES, default="active")

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "абонемент"
        verbose_name_plural = "абонементы"

    def __str__(self):
        return f"Абонемент {self.child.full_name}"

    @property
    def used_classes(self):
        return self.total_classes - self.remaining_classes

    @property
    def progress(self):
        raw = self.used_classes / self.total_classes * 20
        return min(round(raw) * 5, 100)


class Attendance(models.Model):
    STATUS_CHOICES = [("present", "Присутствовал"), ("absent", "Отсутствовал")]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name="занятие")
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="attendance", verbose_name="ребёнок")
    date = models.DateField("дата")
    status = models.CharField("статус", max_length=20, choices=STATUS_CHOICES)

    class Meta:
        ordering = ["-date"]
        verbose_name = "посещение"
        verbose_name_plural = "посещаемость"

    def __str__(self):
        return f"{self.child.full_name} ({self.date:%d.%m.%Y})"


class Payment(models.Model):
    STATUS_CHOICES = [("paid", "Оплачен"), ("waiting", "Ожидает")]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="payments", verbose_name="ребёнок")
    date = models.DateField("дата")
    amount = models.PositiveIntegerField("сумма, ₽")
    purpose = models.CharField("назначение", max_length=120)
    status = models.CharField("статус", max_length=20, choices=STATUS_CHOICES, default="paid")

    class Meta:
        ordering = ["-date"]
        verbose_name = "платёж"
        verbose_name_plural = "платежи"

    def __str__(self):
        return f"{self.child.full_name} · {self.amount} ₽"


class MedicalCertificate(models.Model):
    STATUS_CHOICES = [("pending", "На проверке"), ("approved", "Одобрена"), ("rejected", "Отклонена")]

    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="certificates", verbose_name="абонемент"
    )
    file = models.FileField("файл", upload_to="certificates/")
    upload_date = models.DateTimeField("загружена", auto_now_add=True)
    status = models.CharField("статус", max_length=20, choices=STATUS_CHOICES, default="pending")

    class Meta:
        verbose_name = "медицинская справка"
        verbose_name_plural = "медицинские справки"

    def __str__(self):
        return f"Справка {self.subscription.child.full_name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_status = MedicalCertificate.objects.get(pk=self.pk).status
        super().save(*args, **kwargs)
        if not is_new and old_status != "approved" and self.status == "approved":
            self.subscription.remaining_classes += 1
            self.subscription.end_date += timedelta(days=1)
            self.subscription.save()

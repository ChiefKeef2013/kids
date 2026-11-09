from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

class Child(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    full_name = models.CharField(max_length=200)
    birth_date = models.DateField()

    def get_age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def __str__(self):
        return self.full_name

class Club(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    direction = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    full_name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=200)

    def __str__(self):
        return self.full_name

class Group(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='groups')
    teachers = models.ManyToManyField(Teacher, blank=True)
    min_age = models.IntegerField()
    max_age = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.club.name} - группа"

class Room(models.Model):
    number = models.CharField(max_length=50)
    capacity = models.IntegerField()

    def __str__(self):
        return f"Кабинет {self.number}"

class Schedule(models.Model):
    DAY_CHOICES = [(i, str(i)) for i in range(1,8)]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="schedules")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.group.club.name} (день {self.day_of_week})"

class Subscription(models.Model):
    STATUS_CHOICES = [('active', 'Активен'), ('expired', 'Истёк')]
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='subscriptions')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    remaining_classes = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Абонемент {self.child.full_name}"

class Attendance(models.Model):
    STATUS_CHOICES = [('present', 'Присутствовал'), ('absebt', 'Отсутствовал')]
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.child.full_name} ({self.date})"

class MedicalCertificate(models.Model):
    STATUS_CHOICES = [('pending', 'На проверке'), ('approved', 'Одобрена'), ('rejected', 'Отклонена')]
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='certificates')
    file = models.FileField(upload_to='certificates/')
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        is_new = self.pk in None
        old_status = None
        if not is_new:
            old_instance = MedicalCertificate.objects.get(pk=self.pk)
            old_status = old_instance.status

            super().save(*args, **kwargs)

            if not is_new and old_status != 'approved' and self.status == 'approved':
                self.subscription.remaining_classes += 1
                self.subscription.end_date += timezone.timedelta(days=1)
                self.subscription.save()

    def __str__(self):
        return f"Справка {self.subscription.child.full_name}"
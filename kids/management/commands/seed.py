import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from kids.models import Child, Club, Teacher, Group, Room, Schedule, Subscription, Attendance

class Command(BaseCommand):
    help = 'Generates demo data'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@test.com', 'admin')
        
        parent = User.objects.create_user('parent', 'parent@test.com', 'parent')
        
        club = Club.objects.create(name='Робототехника', description='Сборка роботов', direction='Техника')
        club2 = Club.objects.create(name='Рисование', description='Творчество', direction='Искусство')
        
        teacher1 = Teacher.objects.create(full_name='Иванов И.И.', specialization='Робототехника')
        teacher2 = Teacher.objects.create(full_name='Петрова А.А.', specialization='Рисование')
        
        room1 = Room.objects.create(number='101', capacity=15)
        room2 = Room.objects.create(number='102', capacity=12)
        
        group1 = Group.objects.create(club=club, min_age=7, max_age=10, capacity=15)
        group1.teachers.add(teacher1)
        
        group2 = Group.objects.create(club=club2, min_age=5, max_age=8, capacity=12)
        group2.teachers.add(teacher2)
        
        for i in range(1, 8):
            Schedule.objects.create(group=group1, room=room1, day_of_week=i, start_time='15:00', end_time='16:30')
            Schedule.objects.create(group=group2, room=room2, day_of_week=i, start_time='14:00', end_time='15:30')
        
        child = Child.objects.create(parent=parent, full_name='Сидоров М.М.', birth_date=date(2018, 5, 15))
        
        Subscription.objects.create(
            child=child, 
            group=group1, 
            start_date=date.today(), 
            end_date=date.today() + timedelta(days=30), 
            remaining_classes=8, 
            status='active'
        )
        
        for i in range(35):
            Attendance.objects.create(
                schedule=Schedule.objects.first(),
                child=child,
                date=date.today() - timedelta(days=i),
                status='present' if i % 3 != 0 else 'absent'
            )
            
        self.stdout.write(self.style.SUCCESS('Demo data created successfully'))
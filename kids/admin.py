from django.contrib import admin
from .models import Child, Club, Teacher, Group, Room, Schedule, Subscription, Attendance, MedicalCertificate

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'parent', 'birth_date')
    list_filter = ('parent',)

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'direction')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('club', 'min_age', 'max_age', 'capacity')
    filter_horizontal = ('teachers',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('group', 'room', 'day_of_week', 'start_time', 'end_time')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('child', 'group', 'start_date', 'end_date', 'remaining_classes', 'status')
    list_filter = ('status',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('child', 'schedule', 'date', 'status')

@admin.register(MedicalCertificate)
class MedicalCertificateAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'upload_date', 'status')
    list_filter = ('status',)
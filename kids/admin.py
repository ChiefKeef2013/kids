from django.contrib import admin

from .models import (
    Attendance,
    BookingRequest,
    Child,
    Club,
    ContactRequest,
    Group,
    MasterClass,
    MedicalCertificate,
    NewsletterSubscriber,
    Payment,
    PricePlan,
    Profile,
    Review,
    Room,
    Schedule,
    Subscription,
    Teacher,
)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name", "direction", "age_min", "age_max", "price", "order")
    list_filter = ("direction",)
    search_fields = ("name", "tagline")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialization", "experience_years", "tone")
    search_fields = ("full_name", "specialization")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "club", "age_range", "capacity", "room")
    list_filter = ("club",)
    filter_horizontal = ("teachers",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("group", "day_of_week", "start_time", "end_time", "room")
    list_filter = ("day_of_week", "room")


@admin.register(MasterClass)
class MasterClassAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "start_time", "price", "seats", "seats_taken")
    list_filter = ("date", "cover")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(PricePlan)
class PricePlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "lessons", "is_featured", "order")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "club", "months", "is_published", "order")
    list_filter = ("is_published",)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("parent_name", "child_name", "child_age", "club", "created_at", "is_processed")
    list_filter = ("is_processed", "club")
    search_fields = ("parent_name", "child_name", "phone")


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "topic", "created_at")
    list_filter = ("topic",)


admin.site.register([Room, Child, Subscription, Attendance, Payment, MedicalCertificate, NewsletterSubscriber, Profile])

admin.site.site_header = "Детский центр «Умный ребёнок»"
admin.site.site_title = "Умный ребёнок"
admin.site.index_title = "Управление сайтом"

from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import BookingRequest, Child, Club, Group, MedicalCertificate, Subscription


class ExceptionHandlingTests(TestCase):
    """Негативные проверки занятия 16."""

    def setUp(self):
        self.club = Club.objects.create(
            name="Тестовый кружок",
            slug="test-club-16",
            direction="tech",
            age_min=6,
            age_max=10,
            tagline="Кружок для тестов",
            description="Описание",
            skills="Навык",
            format_text="Формат",
            price=1000,
            lessons_per_week=2,
            cover="robo",
            order=1,
        )

    def test_missing_club_returns_404(self):
        response = self.client.get("/clubs/no-such-club-16/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Такой страницы нет", status_code=404)
        self.assertContains(response, "Поиск по сайту", status_code=404)

    def test_staff_without_permissions_returns_403(self):
        staff = User.objects.create_user(
            username="staff.noaccess.16@example.com",
            email="staff.noaccess.16@example.com",
            password="NoAccess12345!",
            is_staff=True,
        )
        self.client.force_login(staff)
        response = self.client.get("/admin/kids/club/")
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Доступ запрещён", status_code=403)
        self.assertContains(response, "Поиск по сайту", status_code=403)

    def test_invalid_booking_does_not_create_record(self):
        before = BookingRequest.objects.count()
        response = self.client.post(
            "/booking/",
            {
                "parent_name": "Тест Валидации",
                "phone": "123",
                "email": "bad-email",
                "child_name": "Тест",
                "child_age": "6",
                "club": self.club.pk,
                "preferred_day": "",
                "preferred_time": "",
                "comment": "",
                "consent": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Введите телефон в формате")
        self.assertContains(response, "Проверьте адрес")
        self.assertContains(response, "Тест Валидации")
        self.assertEqual(BookingRequest.objects.count(), before)

    def test_certificate_approval_rolls_back_on_mid_operation_error(self):
        parent = User.objects.create_user(username="parent.rollback.16@example.com", password="Demo12345!")
        child = Child.objects.create(parent=parent, full_name="Тестовый Ребёнок", birth_date=date(2018, 1, 1))
        group = Group.objects.create(
            club=self.club,
            title="Группа 1",
            min_age=6,
            max_age=10,
            capacity=10,
        )
        subscription = Subscription.objects.create(
            child=child,
            group=group,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            total_classes=8,
            remaining_classes=8,
        )
        certificate = MedicalCertificate.objects.create(
            subscription=subscription,
            file=SimpleUploadedFile("scan.pdf", b"%PDF-1.4\n%%EOF\n"),
            status="pending",
        )
        with patch("kids.models.Subscription.save", side_effect=RuntimeError("database error")):
            certificate.status = "approved"
            with self.assertRaises(RuntimeError):
                certificate.save()
        certificate.refresh_from_db()
        subscription.refresh_from_db()
        self.assertEqual(certificate.status, "pending")
        self.assertEqual(subscription.remaining_classes, 8)
        self.assertEqual(subscription.end_date, date.today() + timedelta(days=30))

    def test_progress_empty_subscription_does_not_divide_by_zero(self):
        subscription = Subscription(total_classes=0, remaining_classes=0)
        self.assertEqual(subscription.progress, 0)
        self.assertEqual(subscription.used_classes, 0)

    def test_empty_catalog_returns_page_not_error(self):
        response = self.client.get("/clubs/?search=zzzz-no-results")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ничего не нашлось")

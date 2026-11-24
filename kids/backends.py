import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .models import Profile


def _phone_key(value):
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 11 and digits[0] in "78":
        return digits[1:]
    return digits[-10:] if len(digits) >= 10 else digits


class PhoneOrEmailBackend(ModelBackend):
    """Вход по e-mail (он же username) или по номеру телефона из профиля."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(get_user_model().USERNAME_FIELD)
        if username is None or password is None:
            return None

        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user is not None:
            return user

        phone = _phone_key(username)
        if len(phone) < 10:
            return None

        for profile in Profile.objects.select_related("user"):
            if _phone_key(profile.phone) != phone:
                continue
            candidate = profile.user
            if candidate.check_password(password) and self.user_can_authenticate(candidate):
                return candidate
        return None

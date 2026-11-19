import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import BookingRequest, ContactRequest, NewsletterSubscriber, Profile

PHONE_RE = re.compile(r"^\+7 \d{3} \d{3}-\d{2}-\d{2}$")

WIDGET_CLASSES = {
    "TextInput": "input",
    "EmailInput": "input",
    "Textarea": "textarea",
    "Select": "select",
    "PasswordInput": "input",
    "NumberInput": "input",
}


class StyledFormMixin:
    """Проставляет классы полей, чтобы шаблон не зависел от типа виджета."""

    def style_fields(self):
        for field in self.fields.values():
            css = WIDGET_CLASSES.get(field.widget.__class__.__name__)
            if css:
                field.widget.attrs["class"] = f"{field.widget.attrs.get('class', '')} {css}".strip()


class BookingForm(StyledFormMixin, forms.ModelForm):
    """Запись на пробное занятие: поля и сообщения из отчёта занятия 6."""

    class Meta:
        model = BookingRequest
        fields = [
            "parent_name",
            "phone",
            "email",
            "child_name",
            "child_age",
            "club",
            "preferred_day",
            "preferred_time",
            "comment",
            "consent",
        ]
        widgets = {
            "parent_name": forms.TextInput(attrs={"placeholder": "Мария Хасанзянова", "autocomplete": "name"}),
            "phone": forms.TextInput(
                attrs={"placeholder": "+7 900 000-00-00", "inputmode": "tel", "data-mask": "phone"}
            ),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "child_name": forms.TextInput(attrs={"placeholder": "Миша"}),
            "club": forms.Select(),
            "comment": forms.Textarea(
                attrs={"placeholder": "Что важно знать о ребёнке: аллергии, особенности, пожелания", "rows": 4}
            ),
        }
        error_messages = {
            "parent_name": {
                "required": "Укажите имя родителя — так администратор поймёт, к кому обращаться",
                "max_length": "Имя слишком длинное: не больше 60 символов",
            },
            "phone": {
                "required": "Введите телефон в формате +7 900 000-00-00",
                "max_length": "Введите телефон в формате +7 900 000-00-00",
            },
            "child_name": {
                "required": "Напишите, как зовут ребёнка",
                "max_length": "Имя ребёнка слишком длинное: не больше 40 символов",
            },
            "child_age": {"required": "Выберите возраст — от него зависит группа"},
            "club": {"required": "Выберите направление или мастер-класс"},
            "comment": {"max_length": "Слишком длинный комментарий: не больше 500 символов"},
            "consent": {
                "required": "Отметьте согласие на обработку данных — без него мы не можем принять заявку"
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["club"].empty_label = "Выберите направление"
        self.fields["club"].queryset = self.fields["club"].queryset.order_by("order")
        self.fields["email"].error_messages["invalid"] = "Проверьте адрес: в нём нет символа @"
        self.fields["child_age"].choices = [(age, f"{age} лет") for age in range(3, 15)]
        self.fields["child_age"].widget.attrs.update({"class": "select"})
        self.fields["preferred_day"].widget.attrs.update({"class": "select"})
        self.fields["preferred_time"].widget.attrs.update({"class": "select"})
        self.style_fields()

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Введите телефон в формате +7 900 000-00-00")
        return phone


class ContactForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContactRequest
        fields = ["name", "phone", "topic", "message", "consent"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Как к вам обращаться"}),
            "phone": forms.TextInput(attrs={"placeholder": "+7 900 000-00-00", "data-mask": "phone"}),
            "message": forms.Textarea(attrs={"placeholder": "Чем подробнее, тем быстрее ответим", "rows": 5}),
        }
        error_messages = {
            "name": {"required": "Как к вам обращаться?"},
            "phone": {"required": "Введите телефон в формате +7 900 000-00-00"},
            "message": {
                "required": "Напишите сообщение — администратор ответит быстрее",
                "min_length": "Сообщение слишком короткое",
                "max_length": "Слишком длинное сообщение: не больше 1000 символов",
            },
            "consent": {"required": "Отметьте согласие — иначе мы не сможем ответить"},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["topic"].choices = [("", "Выберите тему")] + list(ContactRequest.TOPIC_CHOICES)
        self.fields["message"].widget.attrs.update({"data-minlength": "10"})
        self.style_fields()

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Введите телефон в формате +7 900 000-00-00")
        return phone


class NewsletterForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {"email": forms.EmailInput(attrs={"placeholder": "Ваш e-mail", "aria-label": "Ваш e-mail"})}
        error_messages = {"email": {"invalid": "Проверьте адрес электронной почты"}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()


class RegisterForm(StyledFormMixin, UserCreationForm):
    full_name = forms.CharField(
        label="Имя и фамилия",
        max_length=80,
        widget=forms.TextInput(attrs={"placeholder": "Мария Хасанзянова", "autocomplete": "name"}),
        error_messages={"required": "Укажите имя и фамилию — так проще найти вас в группе"},
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+7 900 000-00-00", "data-mask": "phone"}),
        error_messages={"required": "Введите телефон в формате +7 900 000-00-00"},
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
        error_messages={"invalid": "Проверьте адрес электронной почты"},
    )
    consent = forms.BooleanField(
        label="Согласие на обработку данных",
        error_messages={"required": "Примите правила центра и согласие на обработку данных"},
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Пароль"
        self.fields["password1"].help_text = "Не меньше 8 символов, одна цифра"
        self.fields["password1"].widget.attrs.update({"placeholder": "Не меньше 8 символов"})
        self.fields["password2"].label = "Повторите пароль"
        self.fields["password2"].widget.attrs.update({"placeholder": "Ещё раз"})
        self.fields["password2"].help_text = ""
        self.style_fields()

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(
                "Такой e-mail уже зарегистрирован — войдите или восстановите пароль"
            )
        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Введите телефон в формате +7 900 000-00-00")
        return phone

    def clean_full_name(self):
        name = self.cleaned_data["full_name"].strip()
        if len(name.split()) < 2:
            raise forms.ValidationError("Укажите имя и фамилию — так проще найти вас в группе")
        return name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].lower()
        user.email = user.username
        parts = self.cleaned_data["full_name"].split(maxsplit=1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""
        if commit:
            user.save()
            Profile.objects.create(user=user, phone=self.cleaned_data["phone"])
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.CharField(
        label="E-mail или телефон",
        widget=forms.TextInput(attrs={"placeholder": "you@example.com", "autocomplete": "username"}),
        error_messages={"required": "Введите e-mail или телефон"},
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"placeholder": "Пароль", "autocomplete": "current-password"}),
        error_messages={"required": "Введите пароль"},
    )
    error_messages = {
        "invalid_login": "Неверный e-mail или пароль",
        "inactive": "Аккаунт отключён",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_fields()

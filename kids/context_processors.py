from django.conf import settings


def center_info(request):
    """Общие данные центра для шапки и подвала."""
    return {
        "center": {
            "name": "Умный ребёнок",
            "legal": "ООО «Детский центр „Умный ребёнок“»",
            "phone": "+7 8422 55-14-70",
            "phone_link": "+78422551470",
            "email": "hello@umny-rebenok.ru",
            "address": "Ульяновск, ул. Гончарова, 30/1",
            "hours": "Пн–Сб 09:00–20:00",
            "inn": "7325123456",
        },
        "debug": settings.DEBUG,
    }

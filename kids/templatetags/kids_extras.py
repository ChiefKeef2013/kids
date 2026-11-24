from django import template

register = template.Library()


@register.filter
def ru_plural(value, variants):
    """Русская форма множественного числа: 1 направление, 2 направления, 24 группы."""
    try:
        number = abs(int(value))
    except (TypeError, ValueError):
        return ""

    one, few, many = [item.strip() for item in variants.split(",")]
    if number % 10 == 1 and number % 100 != 11:
        return one
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return few
    return many

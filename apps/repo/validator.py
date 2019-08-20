from django.core.exceptions import ValidationError


def valid_difficulty(n):
    if n > 5 or n <1:
        raise ValidationError("难度介于1到5之间")

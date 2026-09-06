from django.utils import timezone
from django.core.exceptions import ValidationError

def validate_deadline(value):
    if value < timezone.now():
        raise ValidationError('дедлайн должен быть в будущем')
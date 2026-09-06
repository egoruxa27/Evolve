from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import validate_deadline


User = get_user_model()

class Task(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Не начата'
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Выполнена'
        FAILED = 'failed', 'Провалена'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Пользователь'
    )
    title = models.CharField('Задача', max_length=40)
    description = models.TextField('Описание', blank=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED
    )
    created_at = models.DateTimeField('Дата создания задачи', auto_now_add=True)
    completed_at = models.DateTimeField(
        'Дата выполнения задачи',
        blank=True,
        null=True
    )
    deadline = models.DateTimeField('Дедлайн', validators=[validate_deadline])
    xp_reward = models.PositiveSmallIntegerField(
        'Опыт',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100)
        ]
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

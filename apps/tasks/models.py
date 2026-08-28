from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class Task(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Не начата'
        IN_PROGRESS = 'in_progress', 'В процессе'
        COMPLETED = 'completed', 'Выполнена'

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

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

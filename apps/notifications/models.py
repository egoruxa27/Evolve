from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class TelegramAccount(models.Model):
    user = models.OneToOneField(
        User,
        verbose_name='Пользователь',
        related_name='telegram_account',
        on_delete=models.CASCADE,
    )
    telegram_chat_id = models.BigIntegerField(
        'ID чата Telegram',
        unique=True,
    )

    class Meta:
        verbose_name = 'Telegram-аккаунт'
        verbose_name_plural = 'Telegram-аккаунты'

    def __str__(self):
        return self.user


class Notification(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает отправки'
        SENDING = 'sending', 'Отправляется'
        SENT = 'sent', 'Отправлено'
        FAILED = 'failed', 'Ошибка отправки'

    task = models.ForeignKey(
        'tasks.Task',
        verbose_name='Задача',
        related_name='notifications',
        on_delete=models.CASCADE,
    )
    scheduled_at = models.DateTimeField('Запланировано на')
    sent_at = models.DateTimeField(
        'Отправлено',
        null=True,
        blank=True,
    )
    status = models.CharField(
        'Статус',
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['scheduled_at']
        constraints = [
            models.UniqueConstraint(
                fields=['task', 'scheduled_at'],
                name='unique_notification_per_task_schedule',
            ),
        ]

    def __str__(self):
        return self.task

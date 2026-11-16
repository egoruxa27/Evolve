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
    telegram_user_id = models.BigIntegerField(
        'ID чата Telegram',
        unique=True,
    )

    class Meta:
        verbose_name = 'Telegram-аккаунт'
        verbose_name_plural = 'Telegram-аккаунты'

    def __str__(self):
        return str(self.user)
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Электронная почта', unique=True)
    nickname = models.CharField('Никнейм', unique=True, max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    avatar = models.ImageField(
        'Аватарка',
        upload_to='avatars/',
        null=True,
        blank=True
    )
    level = models.PositiveSmallIntegerField(
        'Уровень пользователя',
        default=1
        )
    xp_amount = models.PositiveIntegerField('Опыт пользователя', default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

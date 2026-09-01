from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .manager import UserManager


# class User(AbstractUser):
#     first_name = None
#     last_name = None
#     username = None

#     email = models.EmailField('Электронная почта', unique=True)
#     nickname = models.CharField('Никнейм', max_length=30, unique=True)

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["nickname"]

#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'

#     def __str__(self):
#         return self.email

# TO DO Refactoring models with AbstractBaseUser and create UserManager наследованный от BaseUserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('Электронная почта', unique=True)
    nickname = models.CharField('Никнейм', unique=True, max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

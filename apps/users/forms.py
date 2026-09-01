from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django import forms


User = get_user_model()

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label='Введите адрес электронной почты',
        error_messages={'unique': 'Пользователь с таким адрессом электронной почты уже существует'}
    )
    nickname = forms.CharField(
        label='Придумайте свой никнейм',
        error_messages={'unique': 'Пользователь с таким никнеймом уже существует.',}
    )

    password1 = forms.CharField(label='Придумайте пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'nickname']


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Введите адрес электронной почты')
    password = forms.CharField(label='Введите пароль', widget=forms.PasswordInput)

    error_messages = {'invalid_login': 'Неверная почта или пароль'}


class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['nickname']
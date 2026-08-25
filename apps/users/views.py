from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView

from .forms import RegisterForm, LoginForm
from django.urls import reverse_lazy, reverse

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm
    next_page = reverse_lazy('tasks:list')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')


class RegisterCreateView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')


# class UpdateProfileView(UpdateView):
#     model = User
    # template_name = 
    # form_class = 

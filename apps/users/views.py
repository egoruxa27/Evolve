from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic import CreateView, UpdateView, DetailView

from .forms import RegisterForm, LoginForm, UpdateProfileForm
from django.urls import reverse_lazy

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


class PrifileView(DetailView):
    model = User
    template_name = 'users/profile.html'

    def get_object(self, queryset = None):
        return self.request.user


class ProfileUserView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:profile')
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/change_profile.html'
    form_class = UpdateProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset = None):
        return User.objects.get(pk=self.request.user.pk)
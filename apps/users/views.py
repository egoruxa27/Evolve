from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django_ratelimit.core import is_ratelimited

from .forms import RegisterForm, LoginForm, UpdateProfileForm
from ..mixins import RateLimitPostMixin

User = get_user_model()

class CustomLoginView(RateLimitPostMixin ,LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm
    next_page = reverse_lazy('tasks:list')
    redirect_authenticated_user = True

    ratelimit_rules = [('ip', '5/m'), ('post:username', '5/m')]
    ratelimit_message = 'Слишком много попыток входа. Попробуйте позже'


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')


class RegisterCreateView(RateLimitPostMixin ,CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    ratelimit_rules = [('ip', '5/h')]
    ratelimit_message = 'Слишком много попыток регистрации'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('tasks:list')

        return super().dispatch(request, *args, **kwargs)


class ProfileUserView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'

    def get_object(self, queryset = None):
        return self.request.user


# class ProfileView(LoginRequiredMixin, DetailView):
#     model = User
#     template_name = 'users/profile.html'


class ChangePasswordView(LoginRequiredMixin, RateLimitPostMixin ,PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:profile')

    ratelimit_rules = [('user','5/d')]
    ratelimit_message = 'Слишком много попыток смены пароля'

    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/change_profile.html'
    form_class = UpdateProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset = None):
        return self.request.user
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic import CreateView, UpdateView, DetailView
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .forms import RegisterForm, LoginForm, UpdateProfileForm

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm
    next_page = reverse_lazy('tasks:list')
    redirect_authenticated_user = True

    @method_decorator(ratelimit(
            key='ip',
            rate='5/m',
            method='POST',
            block=True
        ))
    @method_decorator(ratelimit(
        key='post:username',
        rate='5/m',
        method='POST',
        block=True
    ))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')


class RegisterCreateView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('tasks:list')

        return super().dispatch(request, *args, **kwargs)

    @method_decorator(ratelimit(
            key='ip',
            rate='5/d',
            method='POST', 
            block=True
        ))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProfileUserView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'

    def get_object(self, queryset = None):
        return self.request.user


# class ProfileView(LoginRequiredMixin, DetailView):
#     model = User
#     template_name = 'users/profile.html'


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:profile')

    @method_decorator(ratelimit(
                key='user',
                rate='5/d',
                method='POST', 
                block=True
            ))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/change_profile.html'
    form_class = UpdateProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset = None):
        return self.request.user
from django.urls import path

from . import views


app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterCreateView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.PrifileView.as_view(), name='profile'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('change_profile/', views.UpdateProfileView.as_view(), name='change_profile'),
    path('profile/<int:pk>/', views.ProfileUserView.as_view(), name='profile_user')
]
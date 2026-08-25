from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('tasks:list')

    return redirect('users:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect),
    path('users/', include('apps.users.urls')),
    path('tasks/', include('apps.tasks.urls')),
]

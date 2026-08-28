from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('tasks:list')

    return redirect('users:login')

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),
    path('', root_redirect),
    path('users/', include('apps.users.urls')),
    path('tasks/', include('apps.tasks.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + debug_toolbar_urls()

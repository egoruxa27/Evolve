from django.urls import path

from .views import LinkView

app_name = 'telegram'

urlpatterns = [
    path('link/', LinkView.as_view(), name='link')
]

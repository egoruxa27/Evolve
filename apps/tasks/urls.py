from django.urls import path

from . import views


app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='list'),
    path('create/', views.CreateTaskView.as_view(), name='crete')
]
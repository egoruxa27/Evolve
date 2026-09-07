from django.urls import path

from . import views


app_name = 'tasks'

urlpatterns = [
    path('', views.TaskListView.as_view(), name='list'),
    path('history/', views.TaskHistoryView.as_view(), name='history'),
    path('create/', views.CreateTaskView.as_view(), name='create'),
    path('<int:pk>/status/', views.UpdateTaskStatusView.as_view(), name='change_status'),
    path('<int:pk>/detail/', views.TaskDetailView.as_view(), name='detail'),
    path('category/create', views.CreateCategoryView.as_view(), name='create_category')
]
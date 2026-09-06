from django.views.generic import ListView, CreateView, DetailView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import Task
from .forms import CreateTaskForm
from .services import complete_task


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    paginate_by = 5

    def get_queryset(self):
        return (
            Task.objects
            .filter(user=self.request.user, status__in=['not_started', 'in_progress'])
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_history'] = False
        return context


class TaskHistoryView(TaskListView):
    def get_queryset(self):
        return (
            Task.objects
            .filter(user=self.request.user, status__in=['completed', 'failed'])
            .order_by('-completed_at')
        )

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['is_history'] = True
            return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)


class UpdateTaskStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(
            Task,
            pk=pk,
            user=request.user
        )

        complete_task(task, request.user)

        return redirect('tasks:list')


class CreateTaskView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = CreateTaskForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

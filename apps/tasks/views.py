from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import Task, Category
from .forms import CreateTaskForm, CreateCategoryForm
from .services import complete_task


class BaseTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    paginate_by = 5

    status_filter = []

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user, status__in=self.status_filter).order_by('-created_at')

        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_history'] = self.status_filter in (['completed', 'failed'],)
        context['categories'] = Category.objects.filter(
            user=self.request.user
        ).order_by('name')

        category_id = self.request.GET.get('category')
        if category_id:
            context['current_category'] = Category.objects.filter(
                user=self.request.user,
                pk=category_id
            ).first()
        else:
            context['current_category'] = None

        return context


class TaskListView(BaseTaskListView):
    status_filter = ['not_started', 'in_progress']

class TaskHistoryView(BaseTaskListView):
    status_filter = ['completed', 'failed']
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


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categorys/category_list.html'

    def get_queryset(self):
        return (Category.objects.filter(user=self.request.user))


class CreateCategoryView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CreateCategoryForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DeleteCategoryView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('tasks:list')

    def get_object(self, queryset = None):
        return Category.objects.get(pk=self.kwargs['pk'], user=self.request.user)



class UpdateCategoryView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CreateCategoryForm
    success_url = reverse_lazy('tasks:list')
    template_name = 'tasks/create_task.html'

    def get_object(self, queryset = None):
        return Category.objects.get(pk=self.kwargs['pk'], user=self.request.user)
from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import IntegrityError, transaction

from .models import Task, Category
from .forms import CreateTaskForm, CategoryForm
from .services import complete_task, create_category, CategoryLimitReached, MAX_CATEGORIES
from ..mixins import RateLimitPostMixin


class UserFormKwargsMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class BaseTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    paginate_by = 5

    status_filter = []
    ordering_options = {
        'created': '-created_at',
        'deadline': 'deadline',
        'title': 'title',
    }

    def get_queryset(self):
        self.current_sort = self.request.GET.get('sort', 'created')
        if self.current_sort not in self.ordering_options:
            self.current_sort = 'created'

        queryset = Task.objects.filter(
            user=self.request.user,
            status__in=self.status_filter
        ).select_related('category').order_by(
            self.ordering_options[self.current_sort],
            'pk',
        )

        self.current_category = None
        category_id = self.request.GET.get('category')
        if not category_id:
            return queryset

        try:
            category_id = int(category_id)
        except ValueError:
            messages.error(self.request, 'Некорректный идентификатор категории')
            return queryset.none()

        self.current_category = Category.objects.filter(
            user=self.request.user,
            pk=category_id,
        ).first()

        if self.current_category is None:
            messages.error(self.request, 'Такая категория не существует')
            return queryset.none()

        return queryset.filter(category=self.current_category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(
            user=self.request.user
        ).order_by('name')
        context['current_category'] = self.current_category
        context['current_sort'] = self.current_sort
        return context


class TaskListView(BaseTaskListView):
    status_filter = ['not_started', 'in_progress']

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['is_history'] = False
            return context


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

        #mb race condition, check and fix that
        complete_task(task, request.user)

        return redirect('tasks:list')


class CreateTaskView(
    LoginRequiredMixin,
    RateLimitPostMixin,
    UserFormKwargsMixin,
    CreateView
):
    model = Task
    form_class = CreateTaskForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:list')

    ratelimit_group = 'tasks.create'
    ratelimit_rules = (('user', '30/m'),)
    ratelimit_message = 'Превышен лимит созданных задач'
    extra_context = {'submit_label': 'Создать задачу'}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categorys/category_list.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return (
            Category.objects
            .filter(user=self.request.user)
            .order_by('name')
            .prefetch_related('tasks')
        )


class CreateCategoryView(
    LoginRequiredMixin,
    RateLimitPostMixin,
    UserFormKwargsMixin,
    CreateView
):
    model = Category
    form_class = CategoryForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('tasks:category')

    ratelimit_group = 'tasks.category.create'
    ratelimit_rules = (('user', '30/m'),)
    ratelimit_message = 'Превышен лимит создания категорий'
    extra_context = {'submit_label': 'Создать категорию'}

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = create_category(
                    user=self.request.user,
                    name=form.cleaned_data['name'],
                )
        except CategoryLimitReached:
            form.add_error(None, f'Нельзя создать больше {MAX_CATEGORIES} категорий')
            return self.form_invalid(form)
        except IntegrityError as exc:
            diagnostic = getattr(exc.__cause__, 'diag', None)
            if getattr(diagnostic, 'constraint_name', None) != 'unique_category_per_user':
                raise
            form.add_error('name', 'У вас уже есть категория с таким названием.')
            return self.form_invalid(form)

        return redirect(self.get_success_url())


class DeleteCategoryView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('tasks:category')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class UpdateCategoryView(
    LoginRequiredMixin,
    UserFormKwargsMixin,
    UpdateView
):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy('tasks:category')
    template_name = 'tasks/create_task.html'
    extra_context = {'submit_label': 'Обновить категорию'}

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
            try:
                with transaction.atomic():
                    return super().form_valid(form)
            except IntegrityError as exc:
                diagnostic = getattr(exc.__cause__, 'diag', None)
                if getattr(diagnostic, 'constraint_name', None) != 'unique_category_per_user':
                    raise
                form.add_error('name', 'У вас уже есть категория с таким названием.')
                return self.form_invalid(form)

from django import forms

from .models import Task, Category


class CreateTaskForm(forms.ModelForm):
    xp_reward = forms.IntegerField(
        label='Количество опыта за выполнения задачи',
        help_text='Значение должно быть в диапазоне от 1 до 100'
    )
    deadline = forms.DateTimeField(
        label='Дедлайн',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )

    class Meta:
        model = Task
        fields = ('title', 'description', 'deadline', 'xp_reward', 'category')


class CreateCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)
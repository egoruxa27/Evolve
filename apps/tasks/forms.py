from django import forms

from .models import Task


class CreateTaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        label='Дедлайн',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    class Meta:
        model = Task
        fields = ('title', 'description', 'deadline')


class ChangeTaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('status',)
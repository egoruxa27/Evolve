from django import forms

from .models import Task


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description',)


class ChangeTaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('status',)
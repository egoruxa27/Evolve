from django import forms

from .models import Task, Category


MAX_CATEGORIES = 10

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


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        if (
            self.user
            and Category.objects.filter(user=self.user).count() >= MAX_CATEGORIES
        ):
            raise forms.ValidationError(f'нельзя создать больше {MAX_CATEGORIES} категорий')
        
        return cleaned_data

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

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

    class Meta:
        model = Task
        fields = ('title', 'description', 'deadline', 'xp_reward', 'category')


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if self.user and name:
            duplicate = Category.objects.filter(
                user=self.user,
                name=name,
            ).exclude(pk=self.instance.pk).exists()
            if duplicate:
                self.add_error(
                    'name',
                    'У вас уже есть категория с таким названием.',
                )

        return cleaned_data

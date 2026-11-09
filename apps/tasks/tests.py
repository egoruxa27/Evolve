from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.test import TestCase, override_settings

from .models import Category, Task
from .forms import CategoryForm
from .services import complete_task


User = get_user_model()

class TestServices(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@test.com',
            nickname='test'
        )

    def create_task(self, **kwargs):
        defaults = {
            'user': self.user,
            'title': 'test_task',
            'deadline': timezone.now() + timedelta(hours=1),
            'xp_reward': 10,
        }
        defaults.update(kwargs)

        return Task.objects.create(**defaults)

    def test_task_before_deadline(self):
        task = self.create_task()

        complete_task(task, self.user)

        task.refresh_from_db()

        self.assertEqual(task.status, Task.Status.COMPLETED)
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(self.user.xp_amount, task.xp_reward)

    def test_task_after_deadline(self):
        task = self.create_task(
            deadline=timezone.now() - timedelta(hours=1)
        )

        complete_task(task, self.user)

        task.refresh_from_db()

        self.assertEqual(task.status, Task.Status.FAILED)
        self.assertEqual(self.user.xp_amount, 0)

    def test_complete_task_does_not_give_xp_again(self):
        task = self.create_task(status=Task.Status.COMPLETED)

        complete_task(task, self.user)

        task.refresh_from_db()

        self.assertEqual(self.user.xp_amount, 0)

    def test_user_level_up_at_xp_100(self):
        self.user.xp_amount = 95
        self.user.save()

        task = self.create_task()

        complete_task(task, self.user)

        self.user.refresh_from_db()

        self.assertEqual(self.user.level, 2)
        self.assertEqual(self.user.xp_amount, 5)


class TestTaskAccess(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            nickname='user',
        )

        self.other_user = User.objects.create_user(
            email='other@test.com',
            nickname='other',
        )

        self.user_task = Task.objects.create(
            user=self.user,
            title='User task',
            deadline=timezone.now() + timedelta(hours=1),
            xp_reward=10,
        )

        self.other_task = Task.objects.create(
            user=self.other_user,
            title='Other task',
            deadline=timezone.now() + timedelta(hours=1),
            xp_reward = 10
        )

    def test_user_sees_only_own_tasks(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('tasks:list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User task')
        self.assertNotContains(response, 'Other task')

    def test_user_cannot_open_other_users_task(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('tasks:detail', kwargs={'pk': self.other_task.pk})
        )

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('tasks:list'))

        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('tasks:list')}",
        )


class TestTaskCategoryFilter(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='filter@test.com',
            nickname='filter-user',
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Work',
        )
        self.categorized_task = Task.objects.create(
            user=self.user,
            title='Write report',
            deadline=timezone.now() + timedelta(hours=1),
            xp_reward=10,
            category=self.category,
        )
        self.recent_task = Task.objects.create(
            user=self.user,
            title='Plan week',
            deadline=timezone.now() + timedelta(hours=2),
            xp_reward=10,
        )
        Task.objects.filter(pk=self.recent_task.pk).update(
            created_at=timezone.now() + timedelta(days=1),
        )
        self.client.force_login(self.user)

    def test_filters_tasks_and_sets_current_category(self):
        response = self.client.get(
            reverse('tasks:list'),
            {'category': self.category.pk, 'sort': 'title'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['task_list']),
            [self.categorized_task],
        )
        self.assertEqual(response.context['current_category'], self.category)
        self.assertEqual(response.context['current_sort'], 'title')

    def test_sort_options_and_default_order(self):
        for sort, expected_first, expected_sort in (
            ('title', self.recent_task, 'title'),
            ('deadline', self.categorized_task, 'deadline'),
            ('invalid', self.recent_task, 'created'),
        ):
            with self.subTest(sort=sort):
                response = self.client.get(
                    reverse('tasks:list'),
                    {'sort': sort},
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['current_sort'], expected_sort)
                self.assertEqual(response.context['task_list'][0], expected_first)


class TestCategoryForm(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='category@test.com',
            nickname='category-user',
        )

    def test_rejects_duplicate_name_for_same_user(self):
        Category.objects.create(user=self.user, name='Work')

        form = CategoryForm(data={'name': 'Work'}, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_allows_keeping_name_when_editing_category(self):
        category = Category.objects.create(user=self.user, name='Work')

        form = CategoryForm(
            data={'name': 'Work'},
            instance=category,
            user=self.user,
        )

        self.assertTrue(form.is_valid())

    def test_allows_another_users_category_name(self):
        other = User.objects.create_user(
            email='other-category@test.com', nickname='other-category',
        )
        Category.objects.create(user=other, name='Work')

        form = CategoryForm(data={'name': 'Work'}, user=self.user)

        self.assertTrue(form.is_valid())


class TestTaskRateLimit(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                    email='user@test.com',
                    nickname='user',
                )
        self.client.force_login(self.user)

    @override_settings(RATELIMIT_ENABLE=True)
    def test_create_task_status_ratelimit(self):
        url = reverse('tasks:create')
        category = Category.objects.create(user=self.user, name='Test category')
        data = {
            'title': 'Test task',
            'description': 'Test description',
            'deadline': (
                timezone.localtime(timezone.now() + timedelta(days=1))
                .strftime('%Y-%m-%dT%H:%M')
            ),
            'xp_reward': 10,
            'category': category.pk,
        }

        for _ in range(30):
            self.client.post(url, data)

        self.assertEqual(Task.objects.filter(user=self.user).count(), 30)

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        self.assertEqual(Task.objects.filter(user=self.user).count(), 30)

    @override_settings(RATELIMIT_ENABLE=True)
    def test_create_category_ratelimit(self):
        url = reverse('tasks:create_category')

        for index in range(31):
            data = {'name': f'Test category {index}'}
            self.client.post(url, data)

        self.assertEqual(Category.objects.filter(user=self.user).count(), 30)

        response = self.client.post(
            url,
            {'name': 'Test category 30'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)        
        self.assertEqual(Category.objects.filter(user=self.user).count(), 30)

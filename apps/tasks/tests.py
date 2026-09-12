from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.test import TestCase

from .models import Task
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

        self.user.refresh_from_db

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
#TODO: add tests for forms
from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


NON_NORMALIZED_EMAIL = 'test@MAIL.RU'
NORMAILIZED_EMAIL = 'test@mail.ru'
NICKNAME = 'test_nickname'
PASSWORD = 'TestPassword123'

class TestUserManager(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            email=NORMAILIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD
        )
        self.assertEqual(user.email, NORMAILIZED_EMAIL)
        self.assertEqual(user.nickname, NICKNAME)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email=NORMAILIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD
        )
        self.assertEqual(user.email, NORMAILIZED_EMAIL)
        self.assertEqual(user.nickname, NICKNAME)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', nickname=NICKNAME, password=PASSWORD)

    def test_create_superuser_with_is_staff_false_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=NORMAILIZED_EMAIL, nickname=NICKNAME, password=PASSWORD, is_staff=False
            )

    def test_email_is_normalized(self):
        email = NON_NORMALIZED_EMAIL
        user = User.objects.create_user(email=email, nickname=NICKNAME, password=PASSWORD)
        self.assertEqual(user.email, NORMAILIZED_EMAIL)
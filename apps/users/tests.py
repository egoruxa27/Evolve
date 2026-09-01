from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError
from django.test import TestCase

from .forms import LoginForm, RegisterForm


User = get_user_model()

NON_NORMALIZED_EMAIL = 'test@MAIL.RU'
NORMALIZED_EMAIL = 'test@mail.ru'
DIFFERENT_NORMALIZED_EMAIL = 'diferent_test@mail.ru'
NICKNAME = 'test_nickname'
DIFFERENT_NICKNAME = 'diferent_test_nickname'
PASSWORD = 'TestPassword123'
DIFFERENT_PASSWORD = 'DifferentPassword123'
WEAK_PASSWORD = '123123'


class TestUserManager(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email=NORMALIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD,
        )

        self.assertEqual(user.email, NORMALIZED_EMAIL)
        self.assertEqual(user.nickname, NICKNAME)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email=NORMALIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD,
        )

        self.assertEqual(user.email, NORMALIZED_EMAIL)
        self.assertEqual(user.nickname, NICKNAME)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                nickname=NICKNAME,
                password=PASSWORD,
            )

    def test_create_superuser_with_is_staff_false_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email=NORMALIZED_EMAIL,
                nickname=NICKNAME,
                password=PASSWORD,
                is_staff=False,
            )

    def test_email_is_normalized(self):
        user = User.objects.create_user(
            email=NON_NORMALIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD,
        )

        self.assertEqual(user.email, NORMALIZED_EMAIL)


class TestUserModel(TestCase):
    def test_email_is_unique(self):
        User.objects.create_user(
            email=NORMALIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD,
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=NORMALIZED_EMAIL,
                nickname=DIFFERENT_NICKNAME,
                password=PASSWORD,
            )

    def test_nickname_is_unique(self):
        User.objects.create_user(
            email=NORMALIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD,
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email=DIFFERENT_NORMALIZED_EMAIL,
                nickname=NICKNAME,
                password=PASSWORD,
            )


class TestRegisterForm(TestCase):
    def get_valid_data(self):
        return {
            'email': NORMALIZED_EMAIL,
            'nickname': NICKNAME,
            'password1': PASSWORD,
            'password2': PASSWORD,
        }

    def test_valid_form(self):
        form = RegisterForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid())

    def test_weak_password_rejected(self):
        data = self.get_valid_data()
        data['password1'] = WEAK_PASSWORD
        data['password2'] = WEAK_PASSWORD

        form = RegisterForm(data=data)

        self.assertFalse(form.is_valid())

    def test_passwords_mismatch(self):
        data = self.get_valid_data()
        data['password2'] = DIFFERENT_PASSWORD

        form = RegisterForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class TestUserRegister(TestCase):
    def get_valid_data(self):
        return {
            'email': NORMALIZED_EMAIL,
            'nickname': NICKNAME,
            'password1': PASSWORD,
            'password2': PASSWORD,
        }

    def test_user_register(self):
        form = RegisterForm(data=self.get_valid_data())

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.email, NORMALIZED_EMAIL)
        self.assertEqual(user.nickname, NICKNAME)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertTrue(User.objects.filter(email=NORMALIZED_EMAIL).exists())


class TestLoginForm(TestCase):
    def setUp(self):
        User.objects.create_user(
            email=NORMALIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD,
        )

    def get_valid_data(self):
        return {
            'username': NORMALIZED_EMAIL,
            'password': PASSWORD,
        }

    def test_valid_form(self):
        form = LoginForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid())


class TestUserAuthentication(TestCase):
    def setUp(self):
        User.objects.create_user(
            email=NORMALIZED_EMAIL,
            nickname=NICKNAME,
            password=PASSWORD,
        )

    def test_user_login(self):
        user = authenticate(
            email=NORMALIZED_EMAIL,
            password=PASSWORD,
        )

        self.assertIsNotNone(user)

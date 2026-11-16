from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    RATELIMIT_ENABLE=True,
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
)
class LinkViewRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        user = get_user_model().objects.create_user(
            email='link@example.com', nickname='linkuser',
        )
        self.client.force_login(user)

    @patch('apps.telegram.views.generate_telegram_link_code', return_value='12345678')
    def test_generation_is_limited_after_five_posts(self, generate_code):
        url = reverse('telegram:link')
        for _ in range(5):
            self.assertEqual(self.client.post(url).status_code, 200)

        response = self.client.post(url)

        self.assertRedirects(response, url)
        self.assertEqual(generate_code.call_count, 5)

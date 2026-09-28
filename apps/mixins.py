# core/mixins.py
from django.contrib import messages
from django.shortcuts import redirect
from django_ratelimit.core import is_ratelimited


class RateLimitPostMixin:
    ratelimit_rules = []
    ratelimit_group = None
    ratelimit_message = 'Слишком много попыток. Попробуйте позже.'
    ratelimit_redirect_url = None

    def is_rate_limited(self, request):
        group = self.ratelimit_group or self.__class__.__name__
        limited = False

        for key, rate in self.ratelimit_rules:
            if is_ratelimited(
                request,
                group=f'{group}:{key}',
                key=key,
                rate=rate,
                method='POST',
                increment=True,
            ):
                limited = True
        return limited

    def post(self, request, *args, **kwargs):
        if self.is_rate_limited(request):
            messages.error(request, self.ratelimit_message)
            return redirect(self.ratelimit_redirect_url or request.path)
        return super().post(request, *args, **kwargs)
from django.views import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from ..mixins import RateLimitPostMixin
from .services import generate_telegram_link_code




class LinkView(LoginRequiredMixin, RateLimitPostMixin, View):
    ratelimit_group = 'telegram.link'
    ratelimit_rules = (('user', '5/m'),)
    ratelimit_message = 'Слишком много запросов кода. Попробуйте позже.'

    def post(self, request):
        user = self.request.user
        context = {'code': generate_telegram_link_code(user)}
        return render(request, 'telegram/link.html', context)

    def get(self, request):
        context = 'render_page'
        return render(request, 'telegram/link.html')

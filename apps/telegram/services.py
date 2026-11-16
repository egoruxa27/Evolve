import secrets

from django.core.cache import cache


CODE_TTL = 150


def generate_telegram_link_code(user):
    for _ in range(10):
        code = f'{secrets.randbelow(100_000_000):08d}'
        key_link = f'telegram:link{code}'

        if cache.add(key_link, user.pk, timeout=CODE_TTL):
            return code

    raise RuntimeError('Не удалось сгенирировать уникальный код')
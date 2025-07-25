# Задание 1:
# Подумать, какой из видов пагинации более безопасный, чтобы не “светить” явно параметры в запросе.
# Выбрав нужный класс пагинации подключить глобальную пагинацию в проект.
# На одной странице должно располагаться не более 6 объектов.
#
# Задание 2:
# Подключить систему логирования работы включенного сервера в проект для отслеживания логов работы приложения.
# Логи должны загружаться следующим образом:
# - Отдельно логи работы включенного сервера с выводом в консоль
# - Отдельно логи HTTP запросов и их статусов в отдельную папку logs в корне проекта в файл http_logs.log
# - Отдельно логи запросов в базу данных в отдельную папку logs в корне проекта в файл db_logs.log

# Задача 1:
# 1.Создаём собственный класс пагинации:
# myapp/pagination.py

from rest_framework.pagination import CursorPagination

class MyCursorPagination(CursorPagination):
    page_size = 6
    ordering = '-created_at'

# 2. Подключаем глобально в settings.py:

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'myapp.pagination.MyCursorPagination',
    'PAGE_SIZE': 6,
}

# Задача 2:
# Обновляем settings.py:
import os
LOG_DIR = BASE_DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'http_file': {
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'http_logs.log'),
            'formatter': 'verbose',
            'level': 'INFO',
        },
        'db_file': {
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'db_logs.log'),
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['http_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['db_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'http_logger': {
            'handlers': ['http_file'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


# добавим кастомный middleware, который будет логировать все HTTP-запросы
# и их статус — и писать в http_logs.log.
# myapp/middleware.py

import logging
import time

logger = logging.getLogger('http_logger')

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        logger.info(
            '%s %s %s %s %.2f sec',
            request.method,
            request.get_full_path(),
            response.status_code,
            request.META.get('REMOTE_ADDR'),
            duration
        )
        return response

# подключим middleware в settings.py
# в MIDDLEWARE
'myapp.middleware.LogRequestMiddleware',



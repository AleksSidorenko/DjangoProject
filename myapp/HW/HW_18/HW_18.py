# задание: Реализация аутентификации JWT и пермишенов. Глобальная пагинация.
# Цель:
# Настроить JWT (JSON Web Token) аутентификацию с использованием SimpleJWT
# и реализовать пермишены для защиты API.
# Убедитесь, что только авторизованные пользователи могут выполнять определённые действия.
#
# Задание 1: Настройка JWT аутентификации
# Шаги для выполнения:
# Установите djangorestframework-simplejwt.
# Убедитесь, что библиотека djangorestframework-simplejwt установлена.
# Настройте аутентификацию в settings.py.
# Добавьте конфигурации SimpleJWT в settings.py.
# Добавьте маршруты для получения и обновления JWT токенов.
# Настройте маршруты для получения и обновления JWT токенов.
# Проверьте что эндпоинты работают.
# Проверьте что маршруты для получения и обновления JWT токенов работают.

# Задание 2: Реализация пермишенов для API
# Шаги для выполнения:
# Продумайте пермишены.
# Продумайте какие пермишены должны быть на представлениях.
# Примените пермишены к API представлениям.
# Добавьте пермишены ко всем представлениям.
# Проверьте что пермишены работают.
# Проверьте что пермишены работают согласно их настройкам.
#
# Задание 3: Настройка глобальной пагинации в проекте
# Обновить настройки проекта:
# Подключить в настройках проекта Django REST framework глобальную пагинацию,
# выбрав класс пагинации из тех, что рассматривались на занятиях.
# Протестировать эндпоинты:
# Установить для пагинации возврат 5-ти элементов по умолчанию.
# Проверить работу эндпоинтов с добавлением пагинации
#
# Оформление ответа:
# Предоставьте решение: Прикрепите ссылку на гит.
# Скриншоты тестирования: Приложите скриншоты из Postman,
# подтверждающие успешное использование JWT токенов и соблюдение пермишенов при работе с задачами,
# пагинацию страниц при HTTP GET ответах.

# Задача 1, 3:
# добавим JWT-настройки:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'myapp.pagination.MyCursorPagination',
    'PAGE_SIZE': 5,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# добавим маршруты для JWT:
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Задача 2.
# Обновим в DjangoProject/myapp/views.py:
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['name', 'id']
    ordering = ['name']

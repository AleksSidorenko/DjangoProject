# задание: Реализация JWT (SimpleJWT) аутентификации и пермишенов
# Цель:
# Реализовать авторизацию с извлечением текущего пользователя из запроса
# и применение разрешений на уровне объектов.
# Настроить и интегрировать Swagger для автоматической генерации документации API.
#
# Задание 1: Извлечение текущего пользователя из запроса
# Шаги для выполнения:
# Обновите модели, чтобы включить поле owner.
# Обновите модели Task и SubTask для включения поля owner.
# Измените сериализаторы.
# Измените сериализаторы для моделей Task и SubTask для работы с новым полем.
# Переопределите метод perform_create в представлениях.
# Обновите представления для автоматического добавления владельца объекта.
# Создайте представления для получения задач текущего пользователя.
# Реализуйте представление для получения задач, принадлежащих текущему пользователю.
#
# Задание 2: Реализация пермишенов для API
# Шаги для выполнения:
# Создайте пользовательские пермишены.
# Реализуйте пользовательский пермишен для проверки, что пользователь является автором задачи
# или подзадачи.
# Примените пермишены к API представлениям.
# Добавьте пермишены к представлениям для задач и подзадач, чтобы только владельцы могли их изменять или удалять.
#
# Задание 3: Swagger
# Шаги для выполнения:
# Установите drf-yasg.
# Добавьте drf_yasg в settings.
# Настройте маршруты для Swagger в urls.py.
# Просмотр документации.
# Перейдите по URL /swagger/ или /redoc/, чтобы увидеть документацию для вашего API.
# Оформление ответа:
#
# Предоставьте решение: Прикрепите ссылку на гит.
# Скриншоты тестирования: Приложите скриншоты из консоли или Postman,
# подтверждающие успешное извлечение текущего пользователя из запроса,
# соблюдение пермишенов при работе с задачами, реализованную документацию.

# Задача 1:
# Обновим:
# DjangoProject/myapp/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CategoryManager()  # Кастомный менеджер
    all_objects = models.Manager()  # Стандартный менеджер для доступа ко всем записям

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name

User = get_user_model()

class Task(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name='task', blank=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

class SubTask(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subtasks')

    def __str__(self):
        return self.title


# Обновим:
# DjangoProject/myapp/serializers.py

from rest_framework import serializers
from myapp.models import Task, SubTask, Category
from django.utils import timezone


class CategoryCreateSerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True, required=False)  # Добавляем task_count

    class Meta:
        model = Category
        fields = ['id', 'name', 'task_count']  # Добавляем task_count в fields
        read_only_fields = ['id']

    def create(self, validated_data):
        name = validated_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError({"name": "Category with this name already exists."})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        if name != instance.name and Category.objects.filter(name=name).exists():
            raise serializers.ValidationError({"name": "Category with this name already exists."})
        return super().update(instance, validated_data)

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        slug_field='name'
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'categories', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

class SubTaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskCreateSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        slug_field='name'
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'subtasks', 'categories', 'owner']
        read_only_fields = ['id', 'created_at', 'subtasks', 'owner']

class TaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        slug_field='name'
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'categories', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

# Добавим
# myapp/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает безопасные методы всем авторизованным,
    а изменение и удаление — только владельцу.
    """

    def has_object_permission(self, request, view, obj):
        # Безопасные методы — разрешены всегда
        if request.method in permissions.SAFE_METHODS:
            return True
        # Небезопасные — только если пользователь владелец объекта
        return obj.owner == request.user


# Добавми:

### DjangoProject/DjangoProject/urls.py

from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, re_path, include



schema_view = get_schema_view(
   openapi.Info(
      title="Task API",
      default_version='v1',
      description="API документация для Task Management System",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="support@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Обновим
# DjangoProject/myapp/urls.py

from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from myapp.views import MyTasksView

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('hello/', views.hello_alex, name='hello_alex'),
    path('tasks/', views.TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task_detail_update_delete'),
    path('tasks/stats/', views.TaskStatsView.as_view(), name='task_stats'),
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask_list_create'),
    path('subtasks/<int:pk>/', views.SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask_detail_update_delete'),
    path('', include(router.urls)),  # Подключаем маршруты для CategoryViewSet
    path('tasks/my/', MyTasksView.as_view(), name='my-tasks'),
]



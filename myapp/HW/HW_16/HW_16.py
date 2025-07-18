

# Домашнее задание: Реализация CRUD для категорий с использованием ModelViewSet, мягкое удаление.
# Реализовать полный CRUD для модели категорий (Categories) с помощью ModelViewSet,
# добавить кастомный метод для подсчета количества задач в каждой категории.
# Реализовать систему мягкого удаления для категорий.
#
# Задание 1: Реализация CRUD для категорий с использованием ModelViewSet
# Шаги для выполнения:
# 1. Создайте CategoryViewSet, используя ModelViewSet для CRUD операций.
# 2. Добавьте маршрут для CategoryViewSet.
# 3. Добавьте кастомный метод count_tasks используя декоратор @action для подсчета количества задач,
# связанных с каждой категорией.
#
# Задание 2: Реализация мягкого удаления категорий
# Шаги для выполнения:
# 1. Добавьте два новых поля в вашу модель Category, если таких ещё не было.
# - В модели Category добавьте поля is_deleted(Boolean, default False) и deleted_at(DateTime, null=true)
# - Переопределите метод удаления, чтобы он обновлял новые поля
# к соответствующим значениям: is_deleted=True и дата и время на момент “удаления” записи
# 2. Переопределите менеджера модели Category
# - В менеджере модели переопределите метод get_queryset(),
# чтобы он по умолчанию выдавал только те записи, которые не “удалены” из базы.
#
# Оформление ответа:
# 1. Предоставьте решение: Прикрепите ссылку на гит.
# 2. Скриншоты тестирования: Приложите скриншоты из браузера или Postman,
# подтверждающие успешное создание, обновление, получение и удаление данных через API.

# 1. Реализация CRUD для категорий с использованием ModelViewSet
# Шаги:
# Обновим myapp/views.py:
# Заменим CategoryCreateView на CategoryViewSet.
# Добавим метод count_tasks с декоратором @action.
# Обновим myapp/urls.py:
# Заменим маршрут для CategoryCreateView на маршрут для CategoryViewSet с использованием router.

from django.http import HttpResponse
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from myapp.models import Task, SubTask, Category
from myapp.serializers import TaskSerializer, SubTaskCreateSerializer, TaskDetailSerializer, CategoryCreateSerializer
from django.utils import timezone
from django.db.models import Count
from datetime import datetime


def hello_alex(request):
    return HttpResponse("<h1>Hello, Alex</h1>")


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        day = self.request.query_params.get('day', None)
        if day:
            valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            if day.capitalize() not in valid_days:
                return Response({"error": "Invalid day. Use: Monday, Tuesday, etc."},
                                status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(deadline__week_day=valid_days.index(day.capitalize()) + 1)
        return queryset


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'pk'


class TaskStatsView(generics.GenericAPIView):
    def get(self, request):
        total_tasks = Task.objects.count()
        status_counts = Task.objects.values('status').annotate(count=Count('status'))
        overdue_tasks = Task.objects.filter(deadline__lt=timezone.now(),
                                            status__in=['New', 'In progress', 'Pending', 'Blocked']).count()
        stats = {
            "total_tasks": total_tasks,
            "status_counts": {item['status']: item['count'] for item in status_counts},
            "overdue_tasks": overdue_tasks
        }
        return Response(stats)


class SubTaskListCreateView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all().order_by('-created_at')
    serializer_class = SubTaskCreateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        task_title = self.request.query_params.get('task_title', None)
        status = self.request.query_params.get('status', None)

        if task_title:
            queryset = queryset.filter(task__title__icontains=task_title)

        if status:
            if status not in dict(SubTask.STATUS_CHOICES):
                return Response({"error": "Invalid status. Use: New, In progress, Pending, Blocked, Done"},
                                status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(status=status)

        return queryset


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskCreateSerializer
    lookup_field = 'pk'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer

    @action(detail=False, methods=['get'])
    def count_tasks(self, request):
        categories = self.get_queryset().annotate(task_count=Count('task'))
        serializer = self.get_serializer(categories, many=True)
        data = [
            {
                'id': category['id'],
                'name': category['name'],
                'task_count': category['task_count']
            }
            for category in serializer.data
        ]
        return Response(data)

# Объяснение изменений в views.py
# Импорты:
# Добавлен viewsets для ModelViewSet.
# Добавлен action для кастомного метода count_tasks.
# CategoryViewSet:
# Наследуется от ModelViewSet, который автоматически предоставляет CRUD-операции:
# GET /api/categories/ — список категорий.
# POST /api/categories/ — создание категории.
# GET /api/categories/<pk>/ — детали категории.
# PUT /api/categories/<pk>/ — обновление категории.
# DELETE /api/categories/<pk>/ — удаление категории.
# queryset: Все категории (Category.objects.all()).
# serializer_class: Использует CategoryCreateSerializer (с валидацией уникальности name).
# Метод count_tasks:
# Декоратор @action(detail=False, methods=['get'])
# создает эндпоинт /api/categories/count_tasks/, доступный через GET.
# annotate(task_count=Count('task')): Добавляет поле task_count, подсчитывающее количество задач,
# связанных с каждой категорией через ManyToManyField.
# Сериализатор возвращает данные категорий, а мы формируем ответ с полями id, name и task_count.

# Обновляем myapp/urls.py
# Обновим маршруты, чтобы использовать DefaultRouter для CategoryViewSet:
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

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
]

# Объяснение изменений в urls.py
# DefaultRouter:
# Создает маршруты для CategoryViewSet:
# GET/POST /api/categories/ — список и создание.
# GET/PUT/DELETE /api/categories/<pk>/ — детали, обновление, удаление.
# GET /api/categories/count_tasks/ — кастомный метод.
# basename='category': Указывает базовое имя для маршрутов, так как ModelViewSet требует его.
# include(router.urls): Подключает все маршруты, сгенерированные роутером.

# 2. Реализация мягкого удаления категорий
# Шаги:
# Обновим myapp/models.py:
# Добавим поля is_deleted и deleted_at.
# Создадим кастомный менеджер.
# Переопределим метод удаления.
# Создадим миграции для обновления модели.
# Обновим CategoryViewSet для использования мягкого удаления.
# Обновим модель Category:

from django.db import models
from django.utils import timezone

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

    def __str__(self):
        return self.title

# Объяснение изменений в models.py
# Поля:
# is_deleted = models.BooleanField(default=False): Указывает, удалена ли категория (мягкое удаление).
# deleted_at = models.DateTimeField(null=True, blank=True): Хранит дату и время удаления.
# CategoryManager:
# Наследуется от models.Manager.
# Переопределяет get_queryset для возврата только записей с is_deleted=False.
# Менеджеры:
# objects = CategoryManager(): По умолчанию возвращает только "неудаленные" категории.
# all_objects = models.Manager(): Дает доступ ко всем записям, включая удаленные (для админки или восстановления).
# Метод delete:
# Переопределяет стандартное удаление.
# Устанавливает is_deleted=True и deleted_at=timezone.now(), затем сохраняет объект вместо удаления.

# Добавим возможность восстановления или просмотра удаленных категорий,
# можно добавить кастомный метод @action.
# Обновим CategoryViewSet в myapp/views.py:

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer

    @action(detail=False, methods=['get'])
    def count_tasks(self, request):
        categories = self.get_queryset().annotate(task_count=Count('task'))
        serializer = self.get_serializer(categories, many=True)
        data = [
            {
                'id': category['id'],
                'name': category['name'],
                'task_count': category['task_count']
            }
            for category in serializer.data
        ]
        return Response(data)

    @action(detail=False, methods=['get'])
    def deleted(self, request):
        deleted_categories = Category.all_objects.filter(is_deleted=True)
        serializer = self.get_serializer(deleted_categories, many=True)
        return Response(serializer.data)





"""
Задача: Замена функций представлений на Generic Views для задач и подзадач
Используя Generic Views, замените существующие классы представлений для задач (Tasks)
и подзадач (SubTasks) на соответствующие классы для полного CRUD (Create, Read, Update, Delete) функционала.
Агрегирующий эндпойнт для статистики задач оставьте как есть.
Реализуйте, фильтрацию, поиск и сортировку для этих наборов представлений.

1. Замена представлений для задач (Tasks) на Generic Views
Шаги для выполнения:

- Замените классы представлений для задач на Generic Views:
    - Используйте ListCreateAPIView для создания и получения списка задач.
    - Используйте RetrieveUpdateDestroyAPIView для получения, обновления и удаления задач.
- Реализуйте фильтрацию, поиск и сортировку:
    - Реализуйте фильтрацию по полям status и deadline.
    - Реализуйте поиск по полям title и description.
    - Добавьте сортировку по полю created_at.

Задание 2: Замена представлений для подзадач (SubTasks) на Generic Views
Шаги для выполнения:

- Замените классы представлений для подзадач на Generic Views:
    - Используйте ListCreateAPIView для создания и получения списка подзадач.
    - Используйте RetrieveUpdateDestroyAPIView для получения, обновления и удаления подзадач.
- Реализуйте фильтрацию, поиск и сортировку:
    - Реализуйте фильтрацию по полям status и deadline.
    - Реализуйте поиск по полям title и description.
    - Добавьте сортировку по полю created_at.
3. Оформление ответа:
- Предоставьте решение: Прикрепите ссылку на гит.
- Скриншоты тестирования: Приложите скриншоты из браузера или Postman, подтверждающие успешное создание,
  обновление, получение и удаление данных через API.
"""
# 1. Замена представлений для задач (Tasks) на Generic Views
# Шаги:
# Обновляем myapp/views.py:
# Заменяем TaskListView и TaskCreateView на единый класс TaskListCreateView (на основе ListCreateAPIView).
# Заменяем TaskDetailView на TaskRetrieveUpdateDestroyView (на основе RetrieveUpdateDestroyAPIView).
# Настраиваем фильтрацию, поиск и сортировку с помощью django-filter.
# Оставляем TaskStatsView без изменений.
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from myapp.models import Task, SubTask, Category
from myapp.serializers import TaskSerializer, SubTaskCreateSerializer, TaskDetailSerializer, CategoryCreateSerializer
from django.utils import timezone
from django.db.models import Count
from datetime import datetime


def hello_alex(request):
    return HttpResponse("<h1>Hello, Alex</h1>")


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer  # Используем TaskSerializer
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


class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer


# DjangoProject/myapp/serializers.py
from rest_framework import serializers
from myapp.models import Task, SubTask, Category
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'categories']
        read_only_fields = ['id', 'created_at']

class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
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

class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskCreateSerializer(many=True, read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'subtasks', 'categories']
        read_only_fields = ['id', 'created_at', 'subtasks']

class TaskCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'categories']
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value


# 2. Замена представлений для подзадач (SubTasks) на Generic Views
# Шаги
# Обновления уже включены в myapp/views.py выше (SubTaskListCreateView и SubTaskRetrieveUpdateDestroyView).
# Обновляем myapp/urls.py для соответствия новым классам.
from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_alex, name='hello_alex'),
    path('tasks/', views.TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task_detail_update_delete'),
    path('tasks/stats/', views.TaskStatsView.as_view(), name='task_stats'),
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask_list_create'),
    path('subtasks/<int:pk>/', views.SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask_detail_update_delete'),
    path('categories/', views.CategoryCreateView.as_view(), name='category_create'),
]

# 3.
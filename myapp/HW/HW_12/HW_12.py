"""
Домашнее задание: Проект "Менеджер задач" — Создание API для управления задачами
Цель: Освоить работу с Django REST Framework для создания, получения и агрегирования данных,
используя модели задач.

Задание 1: Эндпоинт для создания задачи
Создайте эндпоинт для создания новой задачи.
Задача должна быть создана с полями title, description, status, и deadline.
Шаги для выполнения:
Определите сериализатор для модели Task.
Создайте представление для создания задачи.
Создайте маршрут для обращения к представлению.

Задание 2: Эндпоинты для получения списка задач и конкретной задачи по её ID
Создайте два новых эндпоинта для:
Получения списка задач
Получения конкретной задачи по её уникальному ID
Шаги для выполнения:
Создайте представления для получения списка задач и конкретной задачи.
Создайте маршруты для обращения к представлениям.

Задание 3: Агрегирующий эндпоинт для статистики задач
Создайте эндпоинт для получения статистики задач, таких как общее количество задач,
количество задач по каждому статусу и количество просроченных задач.
Шаги для выполнения:
Определите представление для агрегирования данных о задачах.
Создайте маршрут для обращения к представлению.
Оформите ваш ответ следующим образом:

Код эндпоинтов: Вставьте весь код представлений и маршрутов.
Скриншоты ручного тестирования: Приложите скриншоты консоли или Postman,
подтверждающие успешное выполнение запросов для каждого эндпоинта.
"""

#### 1. Создание файла `myapp/serializers.py`

from rest_framework import serializers
from myapp.models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

#### 2. Обновление файла `myapp/views.py`

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from myapp.models import Task
from myapp.serializers import TaskSerializer
from django.utils import timezone
from django.db.models import Count

def hello_alex(request):
    return HttpResponse("<h1>Hello, Alex</h1>")

class TaskCreateView(APIView):
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

class TaskDetailView(APIView):
    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            serializer = TaskSerializer(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

class TaskStatsView(APIView):
    def get(self, request):
        total_tasks = Task.objects.count()
        status_counts = Task.objects.values('status').annotate(count=Count('status'))
        overdue_tasks = Task.objects.filter(deadline__lt=timezone.now(), status__in=['New', 'In progress', 'Pending', 'Blocked']).count()
        stats = {
            "total_tasks": total_tasks,
            "status_counts": {item['status']: item['count'] for item in status_counts},
            "overdue_tasks": overdue_tasks
        }
        return Response(stats)

#### 3. Обновление файла `myapp/urls.py`

from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_alex, name='hello_alex'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/stats/', views.TaskStatsView.as_view(), name='task_stats'),
]

'''




### Примечания
- **Сериализатор**: `TaskSerializer` включает поля `id`, `title`, `description`, 
`status`, `deadline`, `created_at`. Поля `id` и `created_at` только для чтения.
- **Представления**:
  - `TaskCreateView`: Создает задачу через POST, возвращает 201 при успехе или 400 при ошибке.
  - `TaskListView`: Возвращает список всех задач.
  - `TaskDetailView`: Возвращает задачу по ID или 404, если задача не найдена.
  - `TaskStatsView`: Агрегирует данные (общее количество, количество по статусам, 
  просроченные задачи).
- **Просроченные задачи**: Считаются задачи со статусами "New", "In progress", "Pending", 
"Blocked" и `deadline` раньше текущего времени (`timezone.now()`).
- **Категории**: Не включены в сериализатор, так как задача не требует их. 
Если нужно добавить, уточните, и я обновлю код.
- **Тестирование**:
  - Используйте Postman или `curl` для отправки запросов.
  - Для "скриншотов" сохраните ответы из Postman или консоли.
  - Убедитесь, что `TIME_ZONE = 'Europe/Berlin'` и `USE_TZ = True` учтены 
  для корректной работы с датами.
- **Ошибки**:
  - Если эндпоинты не работают, проверьте, установлен ли DRF 
  (`rest_framework` есть в `requirements.txt`).
  - Если задача не создается, проверьте формат `deadline` (ISO 8601, например, 
  "2025-06-30T15:00:00+02:00").
  
'''
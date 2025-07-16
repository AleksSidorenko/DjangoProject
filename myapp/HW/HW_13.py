"""
Задача: Проект "Менеджер задач" — Создание и настройка сериализаторов и добавление представлений
Цель:
Освоить настройку сериализаторов для работы с подзадачами и категориями, включая переопределение полей,
использование вложенных сериализаторов, методов create и update, а также классы представлений.

1. Переопределение полей сериализатора
Создайте SubTaskCreateSerializer, в котором поле created_at будет доступно только для чтения (read_only).
Шаги для выполнения:
- Определите SubTaskCreateSerializer в файле serializers.py.
- Переопределите поле created_at как read_only.

2. Переопределение методов create и update
Создайте сериализатор для категории CategoryCreateSerializer, переопределив методы create
и update для проверки уникальности названия категории.
Если категория с таким названием уже существует, возвращайте ошибку валидации.
Шаги для выполнения:
- Определите CategoryCreateSerializer в файле serializers.py.
- Переопределите метод create для проверки уникальности названия категории.
- Переопределите метод update для аналогичной проверки при обновлении.

3. Использование вложенных сериализаторов
Создайте сериализатор для TaskDetailSerializer,
который включает вложенный сериализатор для полного отображения связанных подзадач (SubTask).
Сериализатор должен показывать все подзадачи, связанные с данной задачей.
Шаги для выполнения:
- Определите TaskDetailSerializer в файле serializers.py.
- Вложите SubTaskSerializer внутрь TaskDetailSerializer.

4. Валидация данных в сериализаторах
Создайте TaskCreateSerializer и добавьте валидацию для поля deadline, чтобы дата не могла быть в прошлом.
Если дата в прошлом, возвращайте ошибку валидации.
Шаги для выполнения:
- Определите TaskCreateSerializer в файле serializers.py.
- Переопределите метод validate_deadline для проверки даты.

5. Создание классов представлений
Создайте классы представлений для работы с подзадачами (SubTasks), включая создание, получение, обновление
и удаление подзадач. Используйте классы представлений (APIView) для реализации этого функционала.
Шаги для выполнения:
- Создайте классы представлений для создания и получения списка подзадач (SubTaskListCreateView).
- Создайте классы представлений для получения, обновления и удаления подзадач (SubTaskDetailUpdateDeleteView).
- Добавьте маршруты в файле urls.py, чтобы использовать эти классы.

"""
# Добавлено в myapp/serializers.py
from rest_framework import serializers
from myapp.models import Task, SubTask, Category
from django.utils import timezone

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

# 1. Переопределение полей сериализатора
# Добавляем новый класс SubTaskCreateSerializer

class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']


# 2. Переопределение методов create и update
# Добавляем новый класс
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


# 3. Использование вложенных сериализаторов
# Добавляем новый класс
class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskCreateSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'subtasks']
        read_only_fields = ['id', 'created_at', 'subtasks']


# 4. Валидация данных в сериализаторах
# Добавляем новый класс
class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'categories']
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

# 5. Добавлен код для myapp/views.py
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from myapp.models import Task, SubTask
from myapp.serializers import TaskSerializer, SubTaskCreateSerializer, TaskDetailSerializer
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
            serializer = TaskDetailSerializer(task)
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

class SubTaskListCreateView(APIView):
    def get(self, request):
        subtasks = SubTask.objects.all()
        serializer = SubTaskCreateSerializer(subtasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubTaskDetailUpdateDeleteView(APIView):
    def get(self, request, pk):
        try:
            subtask = SubTask.objects.get(pk=pk)
            serializer = SubTaskCreateSerializer(subtask)
            return Response(serializer.data)
        except SubTask.DoesNotExist:
            return Response({"error": "SubTask not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            subtask = SubTask.objects.get(pk=pk)
            serializer = SubTaskCreateSerializer(subtask, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SubTask.DoesNotExist:
            return Response({"error": "SubTask not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            subtask = SubTask.objects.get(pk=pk)
            subtask.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SubTask.DoesNotExist:
            return Response({"error": "SubTask not found"}, status=status.HTTP_404_NOT_FOUND)


# Добавлено два маршрута (Код для myapp/urls.py):
# subtasks/: для получения списка подзадач и создания новых.
# subtasks/<int:pk>/: для получения, обновления и удаления подзадачи по ID.
from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_alex, name='hello_alex'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/stats/', views.TaskStatsView.as_view(), name='task_stats'),
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask_list_create'),
    path('subtasks/<int:pk>/', views.SubTaskDetailUpdateDeleteView.as_view(), name='subtask_detail_update_delete'),
]


# Дополнительно добавлено представление в myapp/views.py
# для категории CategoryCreateSerializer.
class CategoryCreateView(APIView):
    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# И добавлен маршрут в myapp/urls.py:
path('categories/', views.CategoryCreateView.as_view(), name='category_create'),



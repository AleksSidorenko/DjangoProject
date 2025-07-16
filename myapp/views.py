# DjangoProject/myapp/views.py

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from myapp.models import Task, SubTask
from myapp.serializers import TaskSerializer, SubTaskCreateSerializer, TaskDetailSerializer, CategoryCreateSerializer
from django.utils import timezone
from django.db.models import Count
from datetime import datetime


def hello_alex(request):
    return HttpResponse("<h1>Hello, Alex</h1>")

class TaskCreateView(APIView):
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# J,yjdkztv
class TaskListView(APIView):
    def get(self, request):
        day = request.query_params.get('day', None)
        tasks = Task.objects.all()

        if day:
            # Проверяем, что день недели валидный
            valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            if day.capitalize() not in valid_days:
                return Response({"error": "Invalid day. Use: Monday, Tuesday, etc."},
                                status=status.HTTP_400_BAD_REQUEST)
            # Фильтрация по дню недели
            tasks = tasks.filter(deadline__week_day=valid_days.index(day.capitalize()) + 1)

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
        overdue_tasks = Task.objects.filter(deadline__lt=timezone.now(),
                                            status__in=['New', 'In progress', 'Pending', 'Blocked']).count()
        stats = {
            "total_tasks": total_tasks,
            "status_counts": {item['status']: item['count'] for item in status_counts},
            "overdue_tasks": overdue_tasks
        }
        return Response(stats)


class SubTaskListCreateView(APIView):
    def get(self, request):
        task_title = request.query_params.get('task_title', None)
        status = request.query_params.get('status', None)

        subtasks = SubTask.objects.all()

        if task_title:
            subtasks = subtasks.filter(task__title__icontains=task_title)

        if status:
            if status not in dict(SubTask.STATUS_CHOICES):
                return Response({"error": "Invalid status. Use: New, In progress, Pending, Blocked, Done"},
                                status=status.HTTP_400_BAD_REQUEST)
            subtasks = subtasks.filter(status=status)

        subtasks = subtasks.order_by('-created_at')

        # Пагинация
        paginator = PageNumberPagination()  # Явно создаем пагинатор
        paginator.page_size = 5  # Устанавливаем размер страницы
        page = paginator.paginate_queryset(subtasks, request)
        serializer = SubTaskCreateSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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
            return Response({"error": "SubTask not found"}, status=status.HTTP_404_NOT_404_NOT_FOUND)

class CategoryCreateView(APIView):
    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


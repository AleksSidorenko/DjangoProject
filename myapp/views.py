# DjangoProject/myapp/views.py

from django.http import HttpResponse
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from myapp.models import Task, SubTask, Category
from myapp.serializers import (TaskSerializer, SubTaskCreateSerializer,
                               TaskDetailSerializer, CategoryCreateSerializer)
from django.utils import timezone
from django.db.models import Count
from datetime import datetime
from rest_framework.permissions import IsAuthenticatedOrReadOnly


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
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['name', 'id']
    ordering = ['name']

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
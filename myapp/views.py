# DjangoProject/myapp/views.py

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from myapp.models import Task, SubTask
from myapp.serializers import TaskSerializer, SubTaskCreateSerializer, TaskDetailSerializer, CategoryCreateSerializer
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

class CategoryCreateView(APIView):
    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from django.shortcuts import render
# from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from myapp.models import Task
# from myapp.serializers import TaskSerializer
# from django.utils import timezone
# from django.db.models import Count
#
# def hello_alex(request):
#     return HttpResponse("<h1>Hello, Alex</h1>")
#
# class TaskCreateView(APIView):
#     def post(self, request):
#         serializer = TaskSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# class TaskListView(APIView):
#     def get(self, request):
#         tasks = Task.objects.all()
#         serializer = TaskSerializer(tasks, many=True)
#         return Response(serializer.data)
#
# class TaskDetailView(APIView):
#     def get(self, request, pk):
#         try:
#             task = Task.objects.get(pk=pk)
#             serializer = TaskSerializer(task)
#             return Response(serializer.data)
#         except Task.DoesNotExist:
#             return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
#
# class TaskStatsView(APIView):
#     def get(self, request):
#         total_tasks = Task.objects.count()
#         status_counts = Task.objects.values('status').annotate(count=Count('status'))
#         overdue_tasks = Task.objects.filter(deadline__lt=timezone.now(), status__in=['New', 'In progress', 'Pending', 'Blocked']).count()
#         stats = {
#             "total_tasks": total_tasks,
#             "status_counts": {item['status']: item['count'] for item in status_counts},
#             "overdue_tasks": overdue_tasks
#         }
#         return Response(stats)

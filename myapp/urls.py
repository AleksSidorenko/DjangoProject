# DjangoProject/myapp/urls.py

from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from myapp.views import MyTasksView, RegisterView, LogoutView


router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    # Примеры
    path('hello/', views.hello_alex, name='hello_alex'),

    # Tasks
    path('tasks/', views.TaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task_detail_update_delete'),
    path('tasks/stats/', views.TaskStatsView.as_view(), name='task_stats'),
    path('tasks/my/', MyTasksView.as_view(), name='my-tasks'),

    # SubTasks
    path('subtasks/', views.SubTaskListCreateView.as_view(), name='subtask_list_create'),
    path('subtasks/<int:pk>/', views.SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask_detail_update_delete'),

    # Категории через ViewSet
    path('', include(router.urls)),

    # Аутентификация
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

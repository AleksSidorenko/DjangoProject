from django.contrib import admin
from .models import Category, Task, SubTask

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'created_at', 'get_categories')
    list_filter = ('status', 'categories', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_task_title', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'task', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

    def get_task_title(self, obj):
        return obj.task.title
    get_task_title.short_description = 'Task'

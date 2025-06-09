# from django.contrib import admin
# from myapp.models import Category, Task, SubTask
#
# admin.site.register(Category)
# admin.site.register(Task)
# admin.site.register(SubTask)
#

from django.contrib import admin
from myapp.models import Category, Task, SubTask

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Отображаем поле name
    search_fields = ('name',)  # Поиск по имени

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'created_at', 'get_categories')  # Отображаем указанные поля
    list_filter = ('status', 'categories')  # Фильтры по статусу и категориям
    search_fields = ('title', 'description')  # Поиск по названию и описанию
    date_hierarchy = 'deadline'  # Навигация по датам

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'  # Название столбца в админке

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_task_title', 'status', 'deadline', 'created_at')  # Отображаем указанные поля
    list_filter = ('status',)  # Фильтр по статусу
    search_fields = ('title', 'description')  # Поиск по названию и описанию

    def get_task_title(self, obj):
        return obj.task.title
    get_task_title.short_description = 'Task'  # Название столбца для task
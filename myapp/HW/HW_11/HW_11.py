"""
Домашнее задание: Проект "Менеджер задач" — Инлайн формы и Admin actions
Задание 1:
Добавить настройку инлайн форм для админ класса задач.
При создании задачи должна появиться возможность создавать сразу и подзадачу.

Задание 2:
Названия задач могут быть длинными и ухудшать читаемость в Админ панели,
поэтому требуется выводить в списке задач укороченный вариант – первые 10 символов с добавлением «...»,
если название длиннее, при этом при выборе задачи для создания подзадачи должно отображаться полное название.
Необходимо реализовать такую возможность.

Задание 3:
Реализовать свой action для Подзадач, который поможет выводить выбранные
в Админ панели объекты в статус Done

"""
# Для выполнения задачи я обновлю файл `myapp/admin.py`

from django.contrib import admin
from myapp.models import Category, Task, SubTask

# Инлайн-форма для подзадач в админке задач
class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1  # Количество пустых форм для подзадач при создании задачи
    fields = ('title', 'description', 'status', 'deadline')
    show_change_link = True  # Позволяет перейти к редактированию подзадачи

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'status', 'deadline', 'created_at', 'get_categories')
    list_filter = ('status', 'categories', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [SubTaskInline]  # Добавляем инлайн-форму для подзадач

    def short_title(self, obj):
        """Отображает укороченное название задачи (первые 10 символов + '...')"""
        if len(obj.title) > 10:
            return f"{obj.title[:10]}..."
        return obj.title
    short_title.short_description = 'Title'

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Categories'

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_task_title', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'task', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    actions = ['mark_as_done']  # Добавляем пользовательский action

    def get_task_title(self, obj):
        return obj.title  # Полное название задачи отображается
    get_task_title.short_description = 'Task'

    def mark_as_done(self, request, queryset):
        """Action для установки статуса 'Done' для выбранных подзадач"""
        updated = queryset.update(status='Done')
        self.message_user(request, f"{updated} subtask(s) marked as Done.")
    mark_as_done.short_description = "Mark selected subtasks as Done"

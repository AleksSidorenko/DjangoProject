# DjangoProject/myapp/models.py

from django.db import models
from django.utils import timezone

class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CategoryManager()  # Кастомный менеджер
    all_objects = models.Manager()  # Стандартный менеджер для доступа ко всем записям

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name='task', blank=True)

    def __str__(self):
        return self.title

class SubTask(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('In progress', 'In progress'),
        ('Pending', 'Pending'),
        ('Blocked', 'Blocked'),
        ('Done', 'Done'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# from django.db import models
# from django.utils import timezone
#
# class CategoryManager(models.Manager):
#     def get_queryset(self):
#          return super().get_queryset().filter(is_deleted=False)
#
# class Category(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     is_deleted = models.BooleanField(default=False)
#     deleted_at = models.DateTimeField(null=True, blank=True)
#
#     objects = CategoryManager()
#     all_objects = models.Manager()
#
#     def delete(self, *args, **kwargs):
#         self.is_deleted = True
#         self.deleted_at = timezone.now()
#         self.save()
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         ordering = ['name']
#         verbose_name = 'Category'
#         verbose_name_plural = 'Categories'
#         constraints = [
#             models.UniqueConstraint(fields=['name'], name='unique_category_name'),
#         ]
#
# class Task(models.Model):
#     STATUS_CHOICES = [
#         ('New', 'New'),
#         ('In progress', 'In progress'),
#         ('Pending', 'Pending'),
#         ('Blocked', 'Blocked'),
#         ('Done', 'Done'),
#     ]
#
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
#     deadline = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     categories = models.ManyToManyField(Category, related_name='task', blank=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = 'Task'
#         verbose_name_plural = 'Tasks'
#         constraints = [
#             models.UniqueConstraint(fields=['title', 'deadline'], name='unique_task_title_deadline'),
#             models.CheckConstraint(
#                 check=models.Q(deadline__isnull=True) | models.Q(deadline__gte=timezone.now()),
#                 name='task_deadline_future'
#             )
#         ]
#
# class SubTask(models.Model):
#     STATUS_CHOICES = [
#         ('New', 'New'),
#         ('In progress', 'In progress'),
#         ('Pending', 'Pending'),
#         ('Blocked', 'Blocked'),
#         ('Done', 'Done'),
#     ]
#
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
#     deadline = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = 'SubTask'
#         verbose_name_plural = 'SubTasks'
#         constraints = [
#             models.UniqueConstraint(fields=['title', 'task'], name='unique_subtask_title_task'),
#             models.CheckConstraint(
#                 check=models.Q(deadline__isnull=True) | models.Q(deadline__gte=timezone.now()),
#                 name='subtask_deadline_future'
#             )
#         ]



# from django.db import models
#
# class Category(models.Model):
#     name = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table = 'task_manager_category'
#         verbose_name = 'Category'
#         verbose_name_plural = 'Categories'
#         constraints = [
#             models.UniqueConstraint(fields=['name'], name='unique_category_name')
#         ]
#
# class Task(models.Model):
#     STATUS_CHOICES = {
#         'New': 'New',
#         'In progress': 'In progress',
#         'Pending': 'Pending',
#         'Blocked': 'Blocked',
#         'Done': 'Done',
#     }
#     title = models.CharField(max_length=100)
#     description = models.TextField(max_length=500, blank=True)
#     categories = models.ManyToManyField(Category, related_name='tasks')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
#     deadline = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         db_table = 'task_manager_task'
#         verbose_name = 'Task'
#         verbose_name_plural = 'Tasks'
#         ordering = ['-created_at']
#         constraints = [
#             models.UniqueConstraint(fields=['title'], name='unique_task_title')
#         ]
#
# class SubTask(models.Model):
#     STATUS_CHOICES = {
#         'New': 'New',
#         'In progress': 'In progress',
#         'Pending': 'Pending',
#         'Blocked': 'Blocked',
#         'Done': 'Done',
#     }
#     title = models.CharField(max_length=100)
#     description = models.TextField(max_length=500, blank=True)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
#     deadline = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         db_table = 'task_manager_subtask'
#         verbose_name = 'SubTask'
#         verbose_name_plural = 'SubTasks'
#         ordering = ['-created_at']
#         constraints = [
#             models.UniqueConstraint(fields=['title'], name='unique_subtask_title')
#         ]
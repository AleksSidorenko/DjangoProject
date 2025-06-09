from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = {
        'New': 'New',
        'In progress': 'In progress',
        'Pending': 'Pending',
        'Blocked': 'Blocked',
        'Done': 'Done',
    }
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    categories = models.ManyToManyField(Category)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('title', 'deadline')

class SubTask(models.Model):
    STATUS_CHOICES = {
        'New': 'New',
        'In progress': 'In progress',
        'Pending': 'Pending',
        'Blocked': 'Blocked',
        'Done': 'Done',
    }
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
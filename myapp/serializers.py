# DjangoProject/myapp/serializers.py

from rest_framework import serializers
from myapp.models import Task, SubTask, Category
from django.utils import timezone

class CategoryCreateSerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True, required=False)  # Добавляем task_count

    class Meta:
        model = Category
        fields = ['id', 'name', 'task_count']  # Добавляем task_count в fields
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

# Остальные сериализаторы остаются без изменений
class TaskSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        slug_field='name'
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'categories']
        read_only_fields = ['id', 'created_at']

class SubTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskCreateSerializer(many=True, read_only=True)
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        slug_field='name'
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'subtasks', 'categories']
        read_only_fields = ['id', 'created_at', 'subtasks']

class TaskCreateSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False,
        slug_field='name'
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'categories']
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value
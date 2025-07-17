"""
Задача: Работа с параметрами запроса и пагинацией.

1. Написать, или обновить, если уже есть, эндпоинт на получение списка всех задач по дню недели.
- Если никакой параметр запроса не передавался - по умолчанию выводить все записи.
- Если был передан день недели (например вторник) - выводить список задач только на этот день недели.

2. Добавить пагинацию в отображение списка подзадач.
На одну страницу должно отображаться не более 5 объектов.
Отображение объектов должно идти в порядке убывания даты
(от самого последнего добавленного объекта к самому первому)

3. Добавить или обновить, если уже есть, эндпоинт на получение списка всех подзадач по названию главной задачи
и статусу подзадач.

- Если фильтр параметры в запросе не передавались - выводить данные по умолчанию, с учётом пагинации.
- Если бы передан фильтр параметр названия главной задачи - выводить данные по этой главной задаче.
- Если был передан фильтр параметр конкретного статуса подзадачи - выводить данные по этому статусу.
- Если были переданы оба фильтра - выводить данные в соответствии с этими фильтрами.

"""
# 1. Эндпоинт для получения списка задач по дню недели.
# Обновляем TaskListView в myapp/views.py:
# Добавляем обработку параметра day из запроса.
# Используем фильтрацию по дню недели для поля deadline.


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

# 2. Пагинация для списка подзадач.
# Добавляем пагинацию в эндпоинт /subtasks/ с лимитом 5 объектов на страницу.
# Сортируем подзадачи по created_at в порядке убывания (от новых к старым).
# DjangoProject/settings.py - Добавляем настройки пагинации

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5
}

# Обновляем SubTaskListCreateView в myapp/views.py:
class SubTaskListCreateView(APIView):
    def get(self, request):
        subtasks = SubTask.objects.all().order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subtasks, request)
        serializer = SubTaskCreateSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Эндпоинт для фильтрации подзадач по названию главной задачи и статусу
# Обновляем SubTaskListCreateView в myapp/views.py:
# Добавляем обработку параметров task_title и status
class SubTaskListCreateView(APIView):
    def get(self, request):
        task_title = request.query_params.get('task_title', None)
        status = request.query_params.get('status', None)

        subtasks = SubTask.objects.all()

        # Фильтрация по названию главной задачи
        if task_title:
            subtasks = subtasks.filter(task__title__icontains=task_title)

        # Фильтрация по статусу подзадачи
        if status:
            if status not in dict(SubTask.STATUS_CHOICES):
                return Response({"error": "Invalid status. Use: New, In progress, Pending, Blocked, Done"},
                                status=status.HTTP_400_BAD_REQUEST)
            subtasks = subtasks.filter(status=status)

        # Сортировка по created_at (убывание)
        subtasks = subtasks.order_by('-created_at')

        # Пагинация
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subtasks, request)
        serializer = SubTaskCreateSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





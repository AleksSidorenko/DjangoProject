"""
Задача: Проект "Менеджер задач" — ORM запросы
Цель:
Освоение основных операций CRUD (Create, Read, Update, Delete) на примере заданных моделей.
Выполните запросы:
1. Создание записей:
- Task:
    - title: "Prepare presentation".
    - description: "Prepare materials and slides for the presentation".
    - status: "New".
    - deadline: Today's date + 3 days.
- SubTasks для "Prepare presentation":
    - title: "Gather information".
        - description: "Find necessary information for the presentation".
        - status: "New".
        - deadline: Today's date + 2 days.
    - title: "Create slides".
        - description: "Create presentation slides".
        - status: "New".
        - deadline: Today's date + 1 day.
2. Чтение записей:
- Tasks со статусом "New":
    - Вывести все задачи, у которых статус "New".
- SubTasks с просроченным статусом "Done":
    - Вывести все подзадачи, у которых статус "Done", но срок выполнения истек.
3. Изменение записей:
- Измените статус "Prepare presentation" на "In progress".
- Измените срок выполнения для "Gather information" на два дня назад.
- Измените описание для "Create slides" на "Create and format presentation slides".
4. Удаление записей:
- Удалите задачу "Prepare presentation" и все ее подзадачи.

Оформите ответ:
Прикрепите все выполненные запросы (код) и скриншоты с консоли к ответу на домашнее задание
"""

from datetime import timedelta
from django.utils import timezone
from myapp.models import Task, SubTask

# Получаем текущую дату и время с учетом временной зоны Europe/Berlin
now = timezone.now()

# 1. СОЗДАНИЕ ЗАПИСЕЙ
# Создаем задачу "Prepare presentation"
task = Task.objects.create(
    title="Prepare presentation",
    description="Prepare materials and slides for the presentation",
    status="New",
    deadline=now + timedelta(days=3)
)

# Создаем подзадачи для "Prepare presentation"
subtask1 = SubTask.objects.create(
    task=task,
    title="Gather information",
    description="Find necessary information for the presentation",
    status="New",
    deadline=now + timedelta(days=2)
)

subtask2 = SubTask.objects.create(
    task=task,
    title="Create slides",
    description="Create presentation slides",
    status="New",
    deadline=now + timedelta(days=1)
)

print("Created Task:")
print(f"- Title: {task.title}, Status: {task.status}, Deadline: {task.deadline}")
print("Created SubTasks:")
print(f"- Title: {subtask1.title}, Status: {subtask1.status}, Deadline: {subtask1.deadline}")
print(f"- Title: {subtask2.title}, Status: {subtask2.status}, Deadline: {subtask2.deadline}")

# 2. ЧТЕНИЕ ЗАПИСЕЙ
# Задачи со статусом "New"
new_tasks = Task.objects.filter(status="New")
print("\nTasks with status 'New':")
for t in new_tasks:
    print(f"- {t.title} (Status: {t.status}, Deadline: {t.deadline})")

# Подзадачи со статусом "Done" и просроченным дедлайном
expired_done_subtasks = SubTask.objects.filter(
    status="Done",
    deadline__lt=now
)
print("\nExpired 'Done' SubTasks:")
if expired_done_subtasks.exists():
    for st in expired_done_subtasks:
        print(f"- {st.title} (Status: {st.status}, Deadline: {st.deadline})")
else:
    print("- No expired 'Done' SubTasks found")

# 3. ИЗМЕНЕНИЕ ЗАПИСЕЙ
# Изменяем статус задачи "Prepare presentation"
try:
    task = Task.objects.get(title="Prepare presentation")
    task.status = "In progress"
    task.save()
    print("\nUpdated task status:")
    print(f"Task '{task.title}' status changed to '{task.status}'")
except Task.DoesNotExist:
    print("\nError: Task 'Prepare presentation' not found")

# Изменяем дедлайн для "Gather information"
try:
    subtask1 = SubTask.objects.get(title="Gather information")
    subtask1.deadline = now - timedelta(days=2)
    subtask1.save()
    print("\nUpdated subtask deadline:")
    print(f"Subtask '{subtask1.title}' deadline changed to {subtask1.deadline}")
except SubTask.DoesNotExist:
    print("\nError: SubTask 'Gather information' not found")

# Изменяем описание для "Create slides"
try:
    subtask2 = SubTask.objects.get(title="Create slides")
    subtask2.description = "Create and format presentation slides"
    subtask2.save()
    print("\nUpdated subtask description:")
    print(f"Subtask '{subtask2.title}' description changed to '{subtask2.description}'")
except SubTask.DoesNotExist:
    print("\nError: SubTask 'Create slides' not found")

# 4. УДАЛЕНИЕ ЗАПИСЕЙ
# Удаляем задачу "Prepare presentation" и связанные подзадачи
try:
    task = Task.objects.get(title="Prepare presentation")
    task_title = task.title
    task.delete()
    print("\nDeleted task and its subtasks:")
    print(f"Task '{task_title}' and all its subtasks have been deleted")
except Task.DoesNotExist:
    print("\nError: Task 'Prepare presentation' not found")

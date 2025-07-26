# myapp/pagination.py

from rest_framework.pagination import CursorPagination

class MyCursorPagination(CursorPagination):
    page_size = 5
    ordering = '-created_at'  # Последние задачи первыми

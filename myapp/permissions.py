# myapp/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает безопасные методы всем авторизованным,
    а изменение и удаление — только владельцу.
    """

    def has_object_permission(self, request, view, obj):
        # Безопасные методы — разрешены всегда
        if request.method in permissions.SAFE_METHODS:
            return True
        # Небезопасные — только если пользователь владелец объекта
        return obj.owner == request.user

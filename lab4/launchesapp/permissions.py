from rest_framework import permissions
from .getUser import getUserBySession

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySession(request)
        print(f"Permission check: {request.user}")
        return bool(user)


class IsAuthOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySession(request)
        return bool(user) or request.method in permissions.SAFE_METHODS
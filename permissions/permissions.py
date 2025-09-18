from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdminUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff


class IsAdminUserOrViewOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or request.user and request.user.is_staff
        )

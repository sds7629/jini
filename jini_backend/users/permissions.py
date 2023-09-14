from rest_framework.permissions import BasePermission


class IsYour(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permisson(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user == obj.user:
                return True
            return False
        else:
            return False

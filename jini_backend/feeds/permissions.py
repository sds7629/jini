from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import ParseError


class IsWriterorReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user == obj.writer or request.user.is_superuser:
                return True
            return False
        else:
            return False


class FeedOrReviewOwnerOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if (
                request.user == obj.writer
                or request.user == obj.feed.writer
                or request.user.is_superuser
            ):
                return True
            return False
        else:
            return False

from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission

from apps.user.config import UserTypeChoices


class AllowAdminOnly(BasePermission):
    """Permission class that only allows admin users."""

    def has_permission(self, request, view):
        """Checks if the user is an admin."""

        from apps.common.views import RoleBasedPermission

        if request.user:
            if (
                not isinstance(request.user, AnonymousUser)
                and hasattr(request.user, "user_type")
                and (
                    request.user.user_type == UserTypeChoices.admin
                    or request.user.user_type == UserTypeChoices.kitchen
                )
            ):
                return RoleBasedPermission.has_permission(self, request, view)
        return False


class AllowCustomerOnly(BasePermission):
    """Permission class that only allows admin users."""

    def has_permission(self, request, view):
        """Checks if the user is an admin."""

        if user := request.user:
            if not isinstance(user, AnonymousUser) and hasattr(user, "user_type"):
                return user.user_type == UserTypeChoices.customer
        return False


class AllowKitchenOnly(BasePermission):
    """Permission class that only allows kitchen users."""

    def has_permission(self, request, view):
        """Checks if the user is an kitchen."""

        if user := request.user:
            if not isinstance(user, AnonymousUser) and hasattr(user, "user_type"):
                return user.user_type == UserTypeChoices.kitchen
        return False



class RoleBasedPermission(BasePermission):
    """
    Custom permission to check role-based access to features.
    """

    def has_permission(self, request, view):
        from apps.access.config import UserTypeChoices

        if not hasattr(request.user, "user_type") or request.user.user_type != UserTypeChoices.admin:
            return True
        else:
            user_role = request.user.user_role
            if not user_role:
                return False

            feature = getattr(view, "feature", None)

            if not feature:
                return True

            operation_mapping = {"list": "retrieve", "partial_update": "update"}

            operation = view.action if hasattr(view, "action") else "retrieve"
            operation = operation_mapping.get(operation, operation)

            valid_operations = ["create", "retrieve", "update", "delete"]
            if operation not in valid_operations:
                operation = "retrieve"
            return user_role.has_permission(feature, operation)

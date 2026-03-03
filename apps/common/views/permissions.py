from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):
    """
    Dynamic RBAC permission class.

    How it works:
        1. Every view declares a `feature` class attribute
           (e.g. feature = "menu_management").
        2. This permission class maps the DRF action to a CRUD operation
           (list → retrieve, partial_update → update, etc.).
        3. It checks the user's assigned `user_role` to see if the role
           grants that operation on the declared feature.

    If the view has no `feature` attribute, access is allowed (unprotected view).
    If the user has no `user_role` assigned, access is denied.
    """

    # DRF action → CRUD operation mapping
    OPERATION_MAPPING = {
        "list": "retrieve",
        "partial_update": "update",
    }
    VALID_OPERATIONS = {"create", "retrieve", "update", "delete"}

    def has_permission(self, request, view):
        user = request.user

        # Anonymous users are always denied
        if isinstance(user, AnonymousUser):
            return False

        # If the view declares no feature, it is unprotected — allow access
        feature = getattr(view, "feature", None)
        if not feature:
            return True

        # User must have a role assigned
        user_role = getattr(user, "user_role", None)
        if not user_role:
            return False

        # Map DRF action → CRUD operation
        action = getattr(view, "action", "retrieve")
        operation = self.OPERATION_MAPPING.get(action, action)
        if operation not in self.VALID_OPERATIONS:
            operation = "retrieve"

        return user_role.has_permission(feature, operation)

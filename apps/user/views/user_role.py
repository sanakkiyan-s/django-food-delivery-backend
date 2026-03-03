from rest_framework.decorators import action

from apps.common.views.generic import (
    AbstractLookUpFieldMixin,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
)
from apps.common.views.permissions import RoleBasedPermission
from apps.user.models.user_role import Feature, Permission, UserRole
from apps.user.serializer.user_role import (
    FeatureListSerializer,
    PermissionListSerializer,
    RolesListSerializer,
    UserRoleListSerializer,
    UserRoleWriteSerializer,
    FeatureWriteSerializer,
)


class FeatureAPIViewSet(AppModelListAPIViewSet):
    """
    List all registered Features.

    Features are the application modules that can be granted or restricted
    per role (e.g. "menu_management", "order_management").  Admin users query
    this endpoint to populate permission dropdowns when configuring a role.

    Allowed methods: GET /feature/
    """

    feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = FeatureListSerializer
    queryset = Feature.objects.all()
    search_fields = ["identity"]
    ordering_fields = ["identity"]


class FeatureCUDAPIViewSet(AbstractLookUpFieldMixin, AppModelCUDAPIViewSet):
    """
    Create, Update, and Delete Features.

    Allowed methods:
        POST   /feature/manage/          → create
        PUT    /feature/manage/<uuid>/   → update
        DELETE /feature/manage/<uuid>/   → destroy
    """

    feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = FeatureWriteSerializer
    queryset = Feature.objects.all()


class RoleListAPIViewSet(AppModelListAPIViewSet):
    """
    List all active UserRole objects with user counts.

    Used on the "Roles" tab of the admin panel to display a summary table
    showing each role and how many admin users are assigned to it.

    Allowed methods: GET /role/
    """

    # feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = RolesListSerializer
    queryset = UserRole.objects.filter(is_active=True)
    filterset_fields = ["is_active"]
    search_fields = ["identity"]

    all_table_columns = {
        "identity": "Role Name",
        "users": "Users",
        "is_active": "Status",
        "created_at": "Created Date",
    }

    def get_meta_for_table(self) -> dict:
        return {"columns": self.get_table_columns()}


class UserRoleAPIViewSet(
    AbstractLookUpFieldMixin,
    AppModelCUDAPIViewSet,
):
    """
    CUD ViewSet for UserRole — registered via AppSimpleRouter.

    Routes provided by the router:
        POST   /role/manage/          → create
        PUT    /role/manage/<uuid>/   → update
        PATCH  /role/manage/<uuid>/   → partial_update
        DELETE /role/manage/<uuid>/   → destroy
        GET    /role/manage/meta/     → get_meta_for_create (auto from base)
        GET    /role/manage/<uuid>/meta/ → get_meta_for_update (auto from base)

    Create / update payload example:
        {
            "identity": "manager",
            "description": "Restaurant floor manager",
            "permissions": {
                "menu_management":  {"create": true,  "retrieve": true,  "update": true,  "delete": false},
                "order_management": {"create": false, "retrieve": true,  "update": false, "delete": false}
            }
        }

    `permissions` is optional. If omitted on create, all features default to false.
    On update, only the keys present in `permissions` are changed.
    """

    feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = UserRoleWriteSerializer
    queryset = UserRole.objects.prefetch_related("permission_set__feature")

    @action(methods=["GET"], detail=True, url_path="permissions")
    def permissions(self, request, uuid=None):
        """Return all permissions for a specific UserRole across all features."""
        user_role = self.get_object()
        permissions = self.serializer_class().get_all_permissions(user_role)
        return self.send_response(permissions)


class UserRoleDetailAPIViewSet(AbstractLookUpFieldMixin, AppModelRetrieveAPIViewSet):
    """
    Retrieve a single UserRole with full permissions detail.

    Allowed methods: GET /role/<uuid>/
    """

    feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = UserRoleListSerializer
    queryset = UserRole.objects.prefetch_related("permission_set__feature")


class PermissionListAPIViewSet(AppModelListAPIViewSet):
    """
    List all Permission objects.

    Allowed methods: GET /permission/
    """

    feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = PermissionListSerializer
    queryset = Permission.objects.select_related("feature")


class CurrentUserPermissionAPIViewSet(AppModelListAPIViewSet):
    """
    List permissions for the currently authenticated user's role.

    This endpoint does NOT enforce feature-based RBAC because any logged-in
    user should be able to query their own permissions for frontend
    visibility/toggle logic.

    Allowed methods: GET /role/my-permissions/
    """

    serializer_class = PermissionListSerializer

    def get_queryset(self):
        """Filter permissions based on the current user's assigned role."""
        user = self.request.user
        if hasattr(user, "user_role") and user.user_role:
            return Permission.objects.filter(user_role=user.user_role).select_related("feature")
        return Permission.objects.none()

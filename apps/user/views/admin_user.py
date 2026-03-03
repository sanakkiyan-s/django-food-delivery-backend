from apps.common.views.generic import (
    AbstractLookUpFieldMixin,
    AppModelCUDAPIViewSet,
    AppModelListAPIViewSet,
    AppModelRetrieveAPIViewSet,
)
from apps.common.views.permissions import RoleBasedPermission
from apps.user.config import UserTypeChoices
from apps.user.models.user import User
from apps.user.serializer.admin_user import (
    AdminUserCUDSerializer,
    AdminUserDetailSerializer,
    AdminUserListSerializer,
)


class AdminUserListAPIViewSet(AppModelListAPIViewSet):
    """
    List all admin users.

    Returns users where user_type='admin', with their assigned role,
    contact info, and status. Supports search by name/phone and
    filter by is_active.

    Allowed methods: GET /admin-users/
    """

    feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = AdminUserListSerializer
    queryset = User.objects.filter(user_type=UserTypeChoices.admin)
    filterset_fields = ["is_active"]
    search_fields = ["phone_number", "name"]

    all_table_columns = {
        "name": "User Name",
        "role": "Role",
        "phone_number": "Mobile Number",
        "email": "Email",
        "is_active": "Status",
        "created_at": "Created Date",
    }

    def get_meta_for_table(self) -> dict:
        return {"columns": self.get_table_columns()}


class AdminUserDetailAPIViewSet(AbstractLookUpFieldMixin, AppModelRetrieveAPIViewSet):
    """
    Retrieve a single admin user with full details.

    Allowed methods: GET /admin-users/details/<uuid>/
    """

    # feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = AdminUserDetailSerializer
    queryset = User.objects.filter(user_type=UserTypeChoices.admin)


class AdminUserCUDAPIViewSet(AbstractLookUpFieldMixin, AppModelCUDAPIViewSet):
    """
    Create, Update, Delete admin users.

    On create, automatically sets user_type='admin'.
    Accepts user_role FK to assign a role during creation.

    Routes:
        POST   /admin-users/manage/          → create
        PUT    /admin-users/manage/<uuid>/   → update
        PATCH  /admin-users/manage/<uuid>/   → partial_update
        DELETE /admin-users/manage/<uuid>/   → destroy
        GET    /admin-users/manage/meta/     → get_meta_for_create
        GET    /admin-users/manage/<uuid>/meta/ → get_meta_for_update
    """

    feature = "user_role_management"
    permission_classes = [RoleBasedPermission]
    serializer_class = AdminUserCUDSerializer
    queryset = User.objects.filter(user_type=UserTypeChoices.admin)

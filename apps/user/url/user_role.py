from apps.common.router import AppSimpleRouter
from apps.user.views.user_role import (
    CurrentUserPermissionAPIViewSet,
    FeatureAPIViewSet,
    FeatureCUDAPIViewSet,
    PermissionListAPIViewSet,
    RoleListAPIViewSet,
    UserRoleAPIViewSet,
    UserRoleDetailAPIViewSet,
)

router = AppSimpleRouter()

router.register("details", UserRoleDetailAPIViewSet, basename="user-role-detail")
router.register("feature/manage", FeatureCUDAPIViewSet, basename="feature-manage")
router.register("feature", FeatureAPIViewSet, basename="feature")
router.register("manage", UserRoleAPIViewSet, basename="user-role")
router.register("permission", PermissionListAPIViewSet, basename="permission")
router.register("my-permissions", CurrentUserPermissionAPIViewSet, basename="my-permissions")
router.register("", RoleListAPIViewSet, basename="role-list")

urlpatterns = router.urls

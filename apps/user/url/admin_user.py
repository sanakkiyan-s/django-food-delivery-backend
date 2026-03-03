from apps.common.router import AppSimpleRouter
from apps.user.views.admin_user import (
    AdminUserCUDAPIViewSet,
    AdminUserDetailAPIViewSet,
    AdminUserListAPIViewSet,
)

router = AppSimpleRouter()

router.register("details", AdminUserDetailAPIViewSet, basename="admin-user-detail")
router.register("manage", AdminUserCUDAPIViewSet, basename="admin-user-manage")
router.register("", AdminUserListAPIViewSet, basename="admin-user-list")

urlpatterns = router.urls

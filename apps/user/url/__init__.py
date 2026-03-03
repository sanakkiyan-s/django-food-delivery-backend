from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.user.url.auth")),
    path("user/", include("apps.user.url.user")),
    path("role/", include("apps.user.url.user_role")),
    path("admin-users/", include("apps.user.url.admin_user")),
]

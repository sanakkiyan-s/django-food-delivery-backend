from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.user.url.auth")),
    path("user/", include("apps.user.url.user")),
]

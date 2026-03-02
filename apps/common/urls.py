from django.urls import path

from apps.common.views import ServerStatusAPIView

app_name = "common"
API_URL_PREFIX = "api/"

urlpatterns = [
    path(f"{API_URL_PREFIX}server/status/", ServerStatusAPIView.as_view()),
]

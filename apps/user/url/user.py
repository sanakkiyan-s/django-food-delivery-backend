from django.urls import path
from apps.user.views.user import UserMeAPIViewSet,    ProfilePictureUploadAPIView

urlpatterns = [
    path(
        "me/",
        UserMeAPIViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
            }
        ),
        name="user-me",
    ),
    path("upload/profile-picture/", ProfilePictureUploadAPIView.as_view(), name="upload-profile-picture"),
]

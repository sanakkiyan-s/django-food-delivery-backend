from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from apps.common.views.generic import AppModelRetrieveAPIViewSet, AppModelUpdateAPIViewSet
from apps.user.models.user import User
from apps.user.serializer.user import BaseUserDetailSerializer, UserUpdateSerializer

from apps.common.views.generic import get_upload_api_view
from apps.user.models.user import UserProfilePicture
from rest_framework.permissions import IsAuthenticated

class ProfilePictureUploadAPIView(get_upload_api_view(meta_model=UserProfilePicture)):
    """API endpoint to upload User profile pictures."""
    permission_classes = [IsAuthenticated]


class UserMeAPIViewSet(AppModelRetrieveAPIViewSet, AppModelUpdateAPIViewSet):
    """
    API endpoint to retrieve and update the authenticated user's profile.
    Uses generic common views for standard CUD operations + automated meta responses.
    
    Allowed methods: GET, PUT, PATCH
    """

    permission_classes = [IsAuthenticated]

    # Required for DRF GenericAPIView
    queryset = User.objects.all()

    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return BaseUserDetailSerializer

    def get_object(self):
        """
        Return the authenticated user instead of using a typical URL lookup parameter.
        This allows the endpoint to just be `/me/` without passing user IDs.
        """
        return self.request.user

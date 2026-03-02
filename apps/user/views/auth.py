from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.views import AppAPIView
from apps.common.views.generic import get_upload_api_view
from apps.user.models.user import UserProfilePicture
from apps.user.serializer.auth import SendOTPSerializer, VerifyOTPSerializer



class SendOTPAPIView(AppAPIView):
    """
    API endpoint to send an OTP to a provided phone number.
    Rate limited by default settings.
    """

    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        """Handle POST request to generate and send OTP."""

        serializer = self.get_valid_serializer()
        otp = serializer.save()

        # In a real app, do not return the OTP code.
        # It is returned here for easy local testing.
        from django.conf import settings
        debug_data = {"otp_code": otp.otp_code} if settings.DEBUG else {}

        return self.send_response(
            data={"phone_number": otp.phone_number, **debug_data},
            message="OTP sent successfully.",
            status_code=status.HTTP_200_OK,
        )


class VerifyOTPAPIView(AppAPIView):
    """
    API endpoint to verify the phone number and OTP code.
    Returns access and refresh tokens.
    """

    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'verify'

    def post(self, request, *args, **kwargs):
        """Handle POST request to verify OTP."""

        serializer = self.get_valid_serializer()
        result = serializer.save()

        message = "User registered successfully." if result["is_new_user"] else "Login successful."

        return self.send_response(
            data=result,
            message=message,
            status_code=status.HTTP_200_OK,
        )


class AppTokenRefreshView(TokenRefreshView):
    """
    Standard simplejwt TokenRefreshView.
    Can be wrapped in AppAPIView later if standardized response schema is strict.
    """
    pass

class LogoutAPIView(AppAPIView):
    """
    API endpoint to logout the user by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handle POST request to logout."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return self.send_response(
                    data={},
                    message="Refresh token is required.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return self.send_response(
                data={},
                message="Successfully logged out.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            return self.send_response(
                data={"detail": str(e)},
                message="Invalid or expired token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

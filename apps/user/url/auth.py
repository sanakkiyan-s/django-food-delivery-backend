from django.urls import path
from apps.user.views.auth import (
    SendOTPAPIView, 
    VerifyOTPAPIView, 
    AppTokenRefreshView, 
    LogoutAPIView,

)

urlpatterns = [
    path("send-otp/", SendOTPAPIView.as_view(), name="send-otp"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("token/refresh/", AppTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
  
]

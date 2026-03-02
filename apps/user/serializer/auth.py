import logging
import random
import string

from django.core.cache import cache
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.common.serializers.base import AppSerializer
from apps.user.models import User
from apps.user.serializer.user import BaseUserDetailSerializer

logger = logging.getLogger(__name__)


class SendOTPSerializer(AppSerializer):
    """
    Serializer to handle OTP sending.
    Validates the phone number, generates an OTP, and stores it in Redis.
    """

    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        """Validate that the phone number is in a valid format."""

        value = value.strip()
        if not value.startswith("+"):
            value = f"+91{value}"
        return value

    def create(self, validated_data):
        """Generate and store OTP in Redis for the given phone number."""

        phone_number = validated_data["phone_number"]

        # Generate a random 6-digit OTP
        otp_code = "".join(random.choices(string.digits, k=6))

        # Store in Redis with a 5-minute (300 seconds) timeout
        cache_key = f"otp_{phone_number}"
        cache.set(cache_key, otp_code, timeout=300)

        # TODO: In production, replace this with a Celery task
        # that sends the OTP via SMS (Twilio / MSG91 / AWS SNS).
        logger.info(f"OTP generated for {phone_number}: {otp_code}")

        # Return a simple namespace so the view can access .phone_number and .otp_code
        from collections import namedtuple

        OTPResult = namedtuple("OTPResult", ["phone_number", "otp_code"])
        return OTPResult(phone_number=phone_number, otp_code=otp_code)


class VerifyOTPSerializer(AppSerializer):
    """
    Serializer to handle OTP verification via Redis.
    Validates phone_number + otp_code, creates user if new,
    and returns JWT tokens + user profile data.
    """

    phone_number = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(max_length=6, min_length=6)

    def validate_phone_number(self, value):
        """Normalize phone number format."""

        value = value.strip()
        if not value.startswith("+"):
            value = f"+91{value}"
        return value

    def validate(self, attrs):
        """Validate the OTP against the Redis cache."""

        phone_number = attrs["phone_number"]
        otp_code = attrs["otp_code"]

        cache_key = f"otp_{phone_number}"
        stored_otp = cache.get(cache_key)

        if not stored_otp:
            raise serializers.ValidationError(
                {"otp_code": "OTP is expired or invalid. Please request a new OTP."}
            )

        if stored_otp != otp_code:
            raise serializers.ValidationError(
                {"otp_code": "Invalid OTP. Please enter the correct code."}
            )

        return attrs

    def create(self, validated_data):
        """
        Delete OTP from Redis, get or create user,
        and return JWT tokens with user data.
        """

        phone_number = validated_data["phone_number"]
        cache_key = f"otp_{phone_number}"

        # Delete the OTP from Redis so it can't be reused
        cache.delete(cache_key)

        # Get or create user
        user, is_new = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={"is_active": True},
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Serialize user data with request context to generate absolute URLs for images
        request = self.context.get("request")
        user_data = BaseUserDetailSerializer(user, context={"request": request}).data

        return {
            "is_new_user": is_new,
            "user": user_data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        }

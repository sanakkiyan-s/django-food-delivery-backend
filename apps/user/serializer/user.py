from apps.user.models.user import User
from rest_framework import serializers
from apps.common.serializers.base import AppReadOnlyModelSerializer,AppWriteOnlyModelSerializer
from apps.common.serializers.common import BaseFileRetrieveSerializer,BaseIdentitySerializer


class BaseUserSerializer(AppReadOnlyModelSerializer):
    """Base Serializer for User list"""

    profile_picture = BaseFileRetrieveSerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = ["id", "name", "phone_number", "user_type", "is_active", "profile_picture"]


class BaseUserDetailSerializer(BaseUserSerializer):
    """Base Serializer for User list"""

    profile_picture = BaseFileRetrieveSerializer()
    user_role = BaseIdentitySerializer()

    class Meta(BaseUserSerializer.Meta):
        model = BaseUserSerializer.Meta.model
        fields = BaseUserSerializer.Meta.fields + ["email", "date_of_birth", "profile_picture", "user_role"]


class UserUpdateSerializer(AppWriteOnlyModelSerializer):
    """Serializer for updating user profile details."""

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = [
            "name",
            "email",
            "date_of_birth",
            "profile_picture",
        ]

    def update(self, instance, validated_data):
        """Delete the old profile picture (record + file) if a new one is provided."""

        new_profile_picture = validated_data.get("profile_picture")
        old_profile_picture = instance.profile_picture

        # If there's a new picture and it's different from the old one, delete the old one
        if new_profile_picture and old_profile_picture and new_profile_picture != old_profile_picture:
            # Delete file from storage
            if old_profile_picture.file:
                old_profile_picture.file.delete(save=False)
            # Delete the DB record
            old_profile_picture.delete()

        return super().update(instance, validated_data)

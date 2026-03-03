from rest_framework import serializers

from apps.common.serializers.base import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.common.serializers.common import BaseIdentitySerializer
from apps.user.config import UserTypeChoices
from apps.user.models.user import User
from apps.user.models.user_role import UserRole


class AdminUserListSerializer(AppReadOnlyModelSerializer):
    """
    Read-only serializer for listing admin users.
    Returns the user's name, role identity, contact info, and status.
    """

    role = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = ["id", "uuid", "name", "role", "phone_number", "email", "is_active", "created_at"]

    def get_role(self, obj):
        """Get the identity of the user's assigned role."""
        return obj.user_role.identity if obj.user_role else None


class AdminUserDetailSerializer(AppReadOnlyModelSerializer):
    """
    Read-only serializer for retrieving a single admin user with full details.
    """

    user_role = BaseIdentitySerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = [
            "id",
            "uuid",
            "name",
            "phone_number",
            "email",
            "user_type",
            "user_role",
            "is_active",
            "date_of_birth",
            "created_at",
        ]


class AdminUserCUDSerializer(AppWriteOnlyModelSerializer):
    """
    Write serializer for creating and updating admin users.

    On create, sets user_type to 'admin' automatically.
    Accepts a `user_role` FK to assign a role during creation.
    """

    user_role = serializers.PrimaryKeyRelatedField(queryset=UserRole.objects.all(), required=False)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = ["name", "phone_number", "email", "user_role"]
        extra_kwargs = {
            "name": {"required": True},
            "phone_number": {"required": True},
            "email": {"required": False},
            "user_role": {"required": False},
        }

    def __init__(self, *args, **kwargs):
        # Skip forced-required logic from base; we handle via extra_kwargs
        super(AppWriteOnlyModelSerializer, self).__init__(*args, **kwargs)

    def create(self, validated_data):
        """Create a new admin user."""
        validated_data["user_type"] = UserTypeChoices.admin
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update an existing admin user."""
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Return the created/updated admin user details."""
        return AdminUserDetailSerializer(instance, context=self.context).data

    def get_meta(self) -> dict:
        """Meta for CUD API — provides dropdown options for user roles."""
        return {
            "user_role": self.serialize_for_meta(queryset=UserRole.objects.all(), fields=["id", "identity"]),
        }

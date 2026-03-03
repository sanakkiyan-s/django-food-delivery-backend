from rest_framework import serializers

from apps.common.serializers.base import AppReadOnlyModelSerializer, AppWriteOnlyModelSerializer
from apps.common.serializers.common import BaseIdentitySerializer
from apps.user.models.user import User
from apps.user.models.user_role import Feature, Permission, UserRole


class PermissionListSerializer(AppReadOnlyModelSerializer):
    """
    Read-only serializer for listing permissions with full feature details.
    Returns feature id/uuid/identity alongside CRUD flags.
    """

    feature = BaseIdentitySerializer()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Permission
        fields = ["id", "uuid", "feature", "create", "retrieve", "update", "delete"]


class PermissionSerializer(AppReadOnlyModelSerializer):
    """
    Compact read-only serializer for embedding inside UserRole responses.
    Returns the feature identity string and CRUD flags.
    """

    feature = serializers.CharField(source="feature.identity")

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Permission
        fields = ["feature", "create", "retrieve", "update", "delete"]


class FeatureListSerializer(AppReadOnlyModelSerializer):
    """
    Read-only serializer for the Feature model.
    Used inside role details and for feature dropdown listings.
    """

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = Feature
        fields = ["id", "uuid", "identity"]


class FeatureWriteSerializer(AppWriteOnlyModelSerializer):
    """
    Write-only serializer for creating and managing Feature modules.
    """

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = Feature
        fields = ["identity"]
        extra_kwargs = {
            "identity": {"required": True},
        }

    def create(self, validated_data):
        """
        When a new Feature is created, automatically generate default False
        permission records for all existing UserRoles securely so that
        the feature instantly becomes available in the UI.
        """
        feature = super().create(validated_data)
        
        # Bulk create default 'false' permissions for all existing roles
        permissions_to_create = [
            Permission(
                user_role=role, 
                feature=feature,
                create=False,
                retrieve=False,
                update=False,
                delete=False
            )
            for role in UserRole.objects.all()
        ]
        
        if permissions_to_create:
            Permission.objects.bulk_create(permissions_to_create)
            
        return feature


class RolesListSerializer(AppReadOnlyModelSerializer):
    """
    Read-only serializer for listing UserRole objects.
    Returns identity, user count, status, and creation date.
    Used on the Roles table page.
    """

    users = serializers.SerializerMethodField()

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserRole
        fields = ["id", "uuid", "identity", "users", "is_active", "created_at"]

    def get_users(self, obj):
        """Get the count of users assigned to this role."""
        return User.objects.filter(user_role=obj).count()


class UserRoleListSerializer(AppReadOnlyModelSerializer):
    """
    Read-only serializer for listing UserRole objects with full permissions.
    Returns identity, description, and all associated permissions.
    """

    permissions = PermissionSerializer(many=True, source="permission_set")

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = UserRole
        fields = ["id", "uuid", "identity", "description", "is_active", "permissions"]


class UserRoleWriteSerializer(AppWriteOnlyModelSerializer):
    """
    Write-only serializer for creating and updating UserRole objects.

    Accepts an optional `permissions` dict in the format expected by
    `UserRole.update_all_permissions`:

        {
            "<feature_identity>": {
                "create": true,
                "retrieve": true,
                "update": false,
                "delete": false
            },
            ...
        }
    """

    # permissions is an optional free-form dict handled in create/update
    permissions = serializers.DictField(child=serializers.DictField(), required=False, write_only=True)

    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = UserRole
        fields = ["identity", "description", "permissions"]
        extra_kwargs = {
            "identity": {"required": True},
            "description": {"required": False},
            "permissions": {"required": False},
        }

    def __init__(self, *args, **kwargs):
        # Skip AppWriteOnlyModelSerializer's forced-required logic for optional fields.
        # We handle required explicitly via extra_kwargs above.
        super(AppWriteOnlyModelSerializer, self).__init__(*args, **kwargs)

    def _apply_permissions(self, instance, permissions_data):
        """Helper to call the model's bulk-permission update method."""
        if permissions_data:
            instance.update_all_permissions(permissions_data)

    def create(self, validated_data):
        """Create UserRole, then seed default permissions followed by any overrides."""
        permissions_data = validated_data.pop("permissions", None)
        instance = super().create(validated_data)
        # Seed all features with False by default, then override with supplied data
        instance.create_default_permissions(permission_flag=False)
        self._apply_permissions(instance, permissions_data)
        return instance

    def update(self, instance, validated_data):
        """Update UserRole fields and optionally bulk-update permissions."""
        permissions_data = validated_data.pop("permissions", None)
        instance = super().update(instance, validated_data)
        self._apply_permissions(instance, permissions_data)
        return instance

    def to_representation(self, instance):
        """Return full role details (incl. permissions) after write operations."""
        return UserRoleListSerializer(instance, context=self.context).data

    def get_all_permissions(self, instance):
        """Return all permissions of a particular UserRole across all features."""
        permissions_list = []
        for feature in Feature.objects.all():
            permission = Permission.objects.filter(feature=feature, user_role=instance).first()
            if permission:
                permissions_list.append(
                    {
                        "feature": {"identity": feature.identity, "id": feature.id},
                        "create": permission.create,
                        "update": permission.update,
                        "retrieve": permission.retrieve,
                        "delete": permission.delete,
                    }
                )
        return {
            "id": instance.id,
            "uuid": str(instance.uuid),
            "identity": instance.identity,
            "description": instance.description,
            "permissions": permissions_list,
        }

    def get_meta(self) -> dict:
        """Meta for CUD API — provides dropdown options for features and existing roles."""
        return {
            "feature": self.serialize_for_meta(queryset=Feature.objects.all(), fields=["id", "identity"]),
            "user_role": self.serialize_for_meta(queryset=UserRole.objects.all(), fields=["id", "identity"]),
        }

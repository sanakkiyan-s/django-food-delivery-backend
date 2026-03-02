from django.db import models

from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseActiveModel,
    BaseModel,
)


class Feature(BaseModel):
    """
    Model that represents Feature.

    ********************* Model Fields *********************
        PK              - id
        Unique          - uuid, identity
        FK              - created_by, modified_by, deleted_by
        Datetime        - created, modified, deleted
        Boolean         - is_deleted
    """

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)

    def create_default_permissions(self):
        """Function to create default permissions"""

        for user_role in UserRole.objects.all():
            user_role.create_default_permissions(False, self)


class UserRole(BaseActiveModel):
    """
    Model that represents UserRole.

    ********************* Model Fields *********************
        PK              - id
        Unique          - uuid, identity
        FK              - created_by, modified_by, deleted_by
        Datetime        - created, modified, deleted
        Boolean         - is_deleted
    """

    identity = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, unique=True)
    description = models.TextField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def update_permission(self, feature, permissions):
        """Function to update permissions"""

        Permission.objects.filter(user_role=self, feature=feature).delete()
        Permission(user_role=self, feature=feature, **permissions).save()

    def create_default_permissions(self, permission_flag=False, specific_feature=None):
        """Function to create default permissions"""

        permissions = {
            "create": permission_flag,
            "update": permission_flag,
            "retrieve": permission_flag,
            "delete": permission_flag,
        }

        if specific_feature:
            Permission(user_role=self, feature=specific_feature, **permissions).save()
            return

        for feature in Feature.objects.all():
            try:
                Permission(user_role=self, feature=feature, **permissions).save()
            except Exception as error:
                print(error)
                pass

    def has_permission(self, feature, operation):
        """Function to check whether the userrole has particular permisssion for a feature"""

        try:
            permission = Permission.objects.get(user_role=self, feature=feature)
            return getattr(permission, operation, False)
        except Permission.DoesNotExist:
            return False

    def update_all_permissions(self, permissions):
        """Function to update all permissions"""

        for feature, permission in permissions.items():
            feature = Feature.objects.get_or_none(identity=feature)
            if feature:
                self.update_permission(feature, permission)


class Permission(BaseModel):
    """
    Model that represents Permission.

    ********************* Model Fields *********************
        PK              - id
        Unique          - uuid
        FK              - created_by, modified_by, deleted_by, user_role, feature
        Datetime        - created, modified, deleted
        Boolean         - is_deleted, create, update, retrieve, delete
    """

    feature = models.ForeignKey(to=Feature, to_field="identity", on_delete=models.CASCADE, null=True)
    user_role = models.ForeignKey(to=UserRole, on_delete=models.SET_NULL, null=True)
    create = models.BooleanField(default=False)
    update = models.BooleanField(default=False)
    retrieve = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            "feature",
            "user_role",
        )

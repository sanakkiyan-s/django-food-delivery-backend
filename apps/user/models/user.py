from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.user.config import LeadTypeChoice, UserTypeChoices
from apps.common.managers import UserManager
from apps.common.model_fields import AppPhoneNumberField
from apps.common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseActiveModel,
    BaseFileUploadModel,
)


class UserProfilePicture(BaseFileUploadModel):
    """
    Model for store User's profile picture

    ********************* Model Fields *********************
        PK          - id
        Unique      - uuid
        FK          - created_by, modified_by, deleted_by
        Datetime    - created, modified, deleted
        Boolean     - is_deleted
        FileField   - file
    """

    pass


class User(BaseActiveModel, AbstractUser):
    """
    User model for the entire application.
    This models holds data other than auth related data.
    Holds information of user.

    ********************* Model Fields *********************
        PK                  - id
        Unique              - uuid, phone_number, keycloak_id
        FK                  - created_by, modified_by
        Datetime            - created, modified
        Boolean             - is_active
        CharField           - keycloak_id, name, last_name, password
        EmailField          - email
        PhoneNumberField    - phone_number
    """

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = UserManager()

    first_name = None
    last_name = None
    username = None

    email = models.EmailField(unique=True, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    profile_picture = models.ForeignKey(
        UserProfilePicture, on_delete=models.DO_NOTHING, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )
    phone_number = AppPhoneNumberField(unique=True)
    password = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    name = models.CharField(max_length=COMMON_CHAR_FIELD_MAX_LENGTH, **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    user_type = models.CharField(
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH, choices=UserTypeChoices.choices, default=UserTypeChoices.customer
    )
    user_role = models.ForeignKey(
        "user.UserRole",
        on_delete=models.SET_NULL,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    )
    date_of_birth = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)

    def __str__(self):
        return str(self.phone_number)

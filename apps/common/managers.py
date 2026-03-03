from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist, ValidationError
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user model manager where phone_number is the unique identifiers
    for authentication instead of usernames.
    """

    def _create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a user with the given phone_number and password.
        """
        if not phone_number:
            raise ValueError(_("The phone_number is must for user."))
        phone_number = self.normalize_phone_number(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def normalize_phone_number(self, phone_number):
        """
        Normalize the phone_number.
        """
        if isinstance(phone_number, str):
            return phone_number.strip()
        return phone_number
    def create_user(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given phone_number and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(phone_number, password, **extra_fields)

    def get_or_none(self, *args, **kwargs):
        """
        Get the object based on the given **kwargs. If not present returns None.
        Note: Expects a single instance.
        """

        try:
            return self.get(*args, **kwargs)
        # if does not exist or if idiotic values like id=None is passed
        except (
            ObjectDoesNotExist,
            AttributeError,
            ValueError,
            MultipleObjectsReturned,
            ValidationError,  # invalid UUID
        ):
            return None


class BaseObjectManagerQuerySet(QuerySet):
    """
    The main/base manager for the apps models. This is used for including common
    model filters and methods. This is used just to make things DRY.

    This can be used in both ways:
        1. Model.app_objects.custom_method()
        2. Model.app_objects.filter().custom_method()

    Reference:
    https://stackoverflow.com/questions/2163151/custom-queryset-and-manager-without-breaking-dry#answer-21757519

    Usage on the model class
        objects = BaseObjectManagerQuerySet.as_manager()

    Available methods -
        get_or_none
        active,
        inactive,
        alive,
        dead,
        delete,
        hard_delete
    """

    def get_or_none(self, *args, **kwargs):
        """
        Get the object based on the given **kwargs. If not present returns None.
        Note: Expects a single instance.
        """

        try:
            return self.get(*args, **kwargs)
        # if does not exist or if idiotic values like id=None is passed
        except (
            ObjectDoesNotExist,
            AttributeError,
            ValueError,
            MultipleObjectsReturned,
            ValidationError,  # invalid UUID
        ):
            return None

    def delete(self):
        """
        Hard-delete the queryset by calling the default `delete` method
        of the queryset.
        """

        return super().delete()


class BaseActiveObjectMangerQueryset(BaseObjectManagerQuerySet):
    """
    The main/base manager for the apps models. This is used for including common
    model filters and methods. This is used just to make things DRY.

    This can be used in both ways:
        1. Model.app_objects.custom_method()
    """

    def active(self):
        """
        Overridden to set archivable fields. Return a queryset of only the active objects, which have `is_active`
        set to True and `is_deleted` set to False.
        """

        return self.filter(is_active=True)

    def inactive(self):
        """
        Overridden to set archivable fields. Return a queryset of only the inactive objects, which have `is_active`
        set to False and `is_deleted` set to False.
        """

        return self.filter(is_active=False)

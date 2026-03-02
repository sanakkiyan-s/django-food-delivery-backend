import re

from django.utils import timezone
from phonenumbers import NumberParseException, is_valid_number, parse
from rest_framework import serializers


def validate_phone_number(value):
    """
    Validates the phone number format and country code.

    Ensures that the phone number is a valid Indian number (+91).
    Raises a validation error if the format or country code is incorrect.
    """

    try:
        phone = parse(str(value), None)
        if phone.country_code != 91 or not is_valid_number(phone):
            raise serializers.ValidationError("Must be a valid Indian phone number.")
    except NumberParseException:
        raise serializers.ValidationError("Invalid phone number format.")
    return value


def validate_integer_length(length):
    """
    Validates the length of an integer.

    Raises a validation error if the integer has the exact specified length.
    """

    def validator(value):
        """
        Validates the length of the integer.

        Returns the value if it matches the specified length, otherwise raises a validation error.
        """

        value_str = str(value)
        if len(value_str) != length:
            raise serializers.ValidationError(f"Must be exactly {length} digits.")
        return value

    return validator


def validate_gst_number(value):
    """Validate GST number format"""

    if len(value) != 15 or not value.isalnum():
        raise serializers.ValidationError("Invalid GST number format. It must be 15 alphanumeric characters.")
    return value


def validate_unique_phone_number(queryset, phone_number, instance=None):
    """
    Validate that the phone number is unique within the given model.

    Args:
        model: The model to check for uniqueness.
        phone_number: The phone number to validate.
        instance: The current instance being validated (optional).

    Raises:
        serializers.ValidationError: If the phone number is not unique.
    """

    if instance:
        queryset = queryset.exclude(pk=instance.pk)
    if queryset.filter(phone_number=phone_number).exists():
        raise serializers.ValidationError("This phone number is already in exists.")
    return phone_number


def validate_past_date(value):
    """Check if the date is in the Future."""

    if value and value > timezone.localtime(timezone.now()).date():
        raise serializers.ValidationError("Date must be in the past.")
    return value


def validate_future_today_date(value):
    """Check if the date is in the past and today"""

    if value and value < timezone.localtime(timezone.now()).date():
        raise serializers.ValidationError("Date must be in the future or today.")
    return value


def validate_pan_card_number(value):
    """Validate Indian PAN card number format."""

    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    if not re.match(pattern, value):
        raise serializers.ValidationError("Invalid PAN card number format.")
    return value


def validate_percentage(value):
    """Validate that the discount value is between 0 and 100."""

    if value < 0 or value > 100:
        raise serializers.ValidationError("Percentage must be between 0 and 100.")
    return value

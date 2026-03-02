import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_past_date(value):
    """Check if the date is in the Future."""

    if value and value > timezone.localtime(timezone.now()).date():
        raise ValidationError("Date must be in the past.")


def validate_future_today_date(value):
    """Check if the date is in the past and today"""

    if value and value < timezone.localtime(timezone.now()).date():
        raise ValidationError("Date must be in the future or today.")


def validate_pan_card_number(value):
    """Validate Indian PAN card number format."""

    pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
    if not re.match(pattern, value):
        raise ValidationError("Invalid PAN card number format.")


def validate_percentage(value):
    """Validate that the discount value is between 0 and 100."""

    if value < 0 or value > 100:
        raise ValidationError("Percentage must be between 0 and 100.")

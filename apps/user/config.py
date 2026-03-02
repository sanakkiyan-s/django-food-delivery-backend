from django.db import models


class UserTypeChoices(models.TextChoices):
    """Choices for user type."""

    admin = "admin", "Admin"
    customer = "customer", "Customer"
    delivery_partner = "delivery_partner", "Delivery Partner"
    kitchen = "kitchen", "Kitchen"


class LeadTypeChoice(models.TextChoices):
    """Choices for Lead Type."""

    app_login = "app_login", "App Login"
    offline_lead = "offline_lead", "Offline Lead"

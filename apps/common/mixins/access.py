from apps.access.config import UserTypeChoices


class AdminCustomerActiveQuerysetMixin:
    """
    Mixin to filter model queryset based on user type.
        Customer - Only show data with active=True
        Admin - Show all data.
    """

    def get_queryset(self):
        """
        Get the queryset based on user type.
        """

        queryset = super().get_queryset()
        user = self.get_user()
        if user.user_type == UserTypeChoices.customer:
            return queryset.active()
        return queryset

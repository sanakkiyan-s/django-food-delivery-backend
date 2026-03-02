from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView

from apps.common.views.mixins import AppViewMixin


class AppAPIView(AppViewMixin, APIView):
    """
    Common api view class for the entire application. Just a central view to customize
    the output response schema. The entire application will follow this schema.
    """

    sync_action_class = None
    get_object_model = None
    serializer_class = None

    def get_valid_serializer(self, instance=None):
        """Central function to get the valid serializer. Raises exceptions."""

        assert self.serializer_class

        # pylint: disable=not-callable
        serializer = self.serializer_class(
            data=self.request.data,
            context=self.get_serializer_context(),
            instance=instance,
        )
        serializer.is_valid(raise_exception=True)
        return serializer

    def get_serializer_context(self):
        """Central function to pass the serializer context."""

        return {"request": self.get_request()}

    def adopt_sync_action_class(self, instance):
        """
        Given the instance of `BaseSyncAction`, this function will adopt the action
        and will send the necessary responses accordingly. DRY function.
        """

        assert self.sync_action_class

        # pylint: disable=not-callable
        success, result = self.sync_action_class(instance=instance, request=self.get_request()).execute()

        if success:
            return self.send_response(data=result)

        return self.send_error_response(data=result)

    def get_object(self, exception=NotFound, identifier="pk"):
        """
        Suppose you want to list data based on an other model. This
        is a centralized function to do the same.
        """
        if self.get_object_model:
            _object = self.get_object_model.objects.get_or_none(**{identifier: self.kwargs[identifier]})

            if not _object:
                raise exception

            return _object

        return super().get_object()

    def choices_for_meta(self, choices: list):
        """
        Given a list of choices like:
            ['active', ...]

        This will return the following:
            [{'id': 'active', 'identity': 'Active'}, ...]

        This will be convenient for the front end to integrate. Also
        this is considered as a standard.
        """

        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]


class AppCreateAPIView(AppViewMixin, CreateAPIView):
    """App's version on the `CreateAPIView`, implements custom handlers."""

    def perform_create(self, serializer):
        """Overridden to call the post create handler."""

        instance = serializer.save()
        self.perform_post_create(instance=instance)

    def perform_post_create(self, instance):
        """Called after `perform_create`. Handle custom logic here."""

        pass

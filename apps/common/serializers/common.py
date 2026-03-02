from rest_framework import serializers

from apps.user.models.user import User
from apps.common.serializers import AppReadOnlyModelSerializer


class SimpleUserSerializer(AppReadOnlyModelSerializer):
    """
    Serializer to display simple user details.
    """

    full_name = serializers.CharField(source="get_full_name")

    class Meta(AppReadOnlyModelSerializer.Meta):
        model = User
        fields = ["id", "uuid", "full_name"]


class BaseIdentitySerializer(serializers.Serializer):
    """Base serializer for id and identity"""

    id = serializers.IntegerField()
    identity = serializers.CharField()


class BaseFileRetrieveSerializer(serializers.Serializer):
    """Base Serializer for id and Image url"""

    id = serializers.IntegerField()
    file = serializers.CharField(source="get_file")


class BaseIdentityImageSerializer(serializers.Serializer):
    """Base serializer for id and identity and file"""

    id = serializers.IntegerField()
    identity = serializers.CharField()
    image = BaseFileRetrieveSerializer()

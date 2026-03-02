from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import ValidationError

from apps.administration.config import UpdateStatusChoice
from apps.administration.models import UploadFile


def save_uploads_on_s3(file_content, upload_record):
    """Function to save the export CSV file in S3 using an in-function serializer."""

    class _UploadFileSerializer(serializers.ModelSerializer):
        class Meta:
            model = UploadFile
            fields = ["file"]

        def create(self, validated_data):
            return UploadFile.objects.create(**validated_data)

    current_datetime = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M%S")
    file_name = f"report_{current_datetime}.csv"
    # check if the received file content is bytesio/stringio
    if isinstance(file_content, bytes):
        content_file = ContentFile(file_content, name=file_name)
    else:
        content_file = ContentFile(file_content.getvalue().encode("utf-8"), name=file_name)
    # save using serializer
    serializer = _UploadFileSerializer(data={"file": content_file})
    if serializer.is_valid():
        report_file = serializer.save()
    else:
        raise ValidationError(serializer.errors)

    # Update the export record
    upload_record.error_file = report_file
    upload_record.status = UpdateStatusChoice.partially_success
    upload_record.save()

    return upload_record

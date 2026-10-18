from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .validators import normalize_phone_number


class PhoneNumberField(serializers.CharField):
    """Validates an Iranian mobile number and converts it to the stored format."""

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        try:
            return normalize_phone_number(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .fields import PhoneNumberField

User = get_user_model()

PHONE_NUMBER_TAKEN_MESSAGE = "A user with this phone number already exists."


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number"]
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(PHONE_NUMBER_TAKEN_MESSAGE)
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return User.objects.create_user(**validated_data)
        except IntegrityError:
            # Another request registered the same number between validation and insert.
            raise serializers.ValidationError({"phone_number": [PHONE_NUMBER_TAKEN_MESSAGE]})


class LoginSerializer(TokenObtainPairSerializer):
    """Same as simplejwt's serializer, but accepts any supported phone number format."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = PhoneNumberField(write_only=True)

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True)

    def validate_refresh(self, value):
        try:
            # امضا، انقضا، نوع توکن و blacklist بودن را چک می‌کند
            return RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token.")

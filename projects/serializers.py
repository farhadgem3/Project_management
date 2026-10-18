from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.fields import PhoneNumberField

from .models import Membership, Project

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]


class MembershipSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user", "phone_number", "role"]
        read_only_fields = fields


class AddMemberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    role = serializers.ChoiceField(choices=Membership.Role.choices)

    def validate(self, attrs):
        try:
            attrs["user"] = User.objects.get(phone_number=attrs["phone_number"])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"phone_number": ["No user with this phone number exists."]}
            )
        return attrs

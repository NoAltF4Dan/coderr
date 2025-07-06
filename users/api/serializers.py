from rest_framework import serializers
from ..models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="id", read_only=True)
    file = serializers.ImageField(required=False, allow_null=True)
    type = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at"
        ]
        read_only_fields = ["user", "created_at", "type"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        optional_fields = [
            "first_name", "last_name", "location",
            "tel", "description", "working_hours"
        ]
        data.update({field: data.get(field) or "" for field in optional_fields})
        return data

    def validate(self, data):
        if self.instance and self.instance.type not in ["business", "customer"]:
            raise serializers.ValidationError("Invalid user type.")
        return data

class BusinessProfileListOutputSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type"
        ]
        read_only_fields = fields
        
class BusinessProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type"
        ]

class CustomerProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="id", read_only=True)
    uploaded_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type"
        ]

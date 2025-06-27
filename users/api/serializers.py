from rest_framework import serializers
from ..models import CustomUser

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'type',
            'location',
            'tel',
            'description',
            'working_hours',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Felder nie null, sondern leerer String, wie in deiner Doku
        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            if data[field] is None:
                data[field] = ''
        return data

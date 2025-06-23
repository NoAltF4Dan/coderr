from rest_framework import serializers
from .models import Offer, OfferDetail

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = "__all__"
        read_only_fields = ["id", "offer"]

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = "__all__"
        read_only_fields = ["id", "user"]

    def validate_details(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Ein Offer muss mindestens 3 Details enthalten.")
        return value
    
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(user=self.context['request'].user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

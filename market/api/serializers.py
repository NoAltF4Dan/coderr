from rest_framework import serializers
from django.db import models
from ..models import Offer, OfferDetail, Order, Review

class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/api/offerdetails/{obj.id}/"

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = "__all__"
        read_only_fields = ["id", "offer"]

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    details_data = OfferDetailSerializer(many=True, write_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at",
            "details", "details_data",
            "details", "min_price", "min_delivery_time", "user_details"
        ]
        read_only_fields = ["id", "user"]

    def get_min_price(self, obj):
        return obj.details.aggregate(models.Min("price"))["price__min"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name or "",
            "last_name": obj.user.last_name or "",
            "username": obj.user.username
        }

    def validate_details(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Ein Offer muss mindestens 3 Details enthalten.")
        return value

    def create(self, validated_data):
        details_data = validated_data.pop("details_data", [])
        offer = Offer.objects.create(user=self.context['request'].user, **validated_data)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if details_data:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                offer_detail = instance.details.filter(offer_type=offer_type).first()
                if offer_detail:
                    offer_detail.title = detail_data.get('title', offer_detail.title)
                    offer_detail.revisions = detail_data.get('revisions', offer_detail.revisions)
                    offer_detail.delivery_time_in_days = detail_data.get('delivery_time_in_days', offer_detail.delivery_time_in_days)
                    offer_detail.price = detail_data.get('price', offer_detail.price)
                    offer_detail.features = detail_data.get('features', offer_detail.features)
                    offer_detail.save()

        return instance


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "created_at", "updated_at", "status", "offer_detail"  # add this line
        ]

    def create(self, validated_data):
        offer_detail_id = validated_data.pop("offer_detail_id")
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)

        user = self.context['request'].user
        order = Order.objects.create(
            customer_user=user,
            business_user=offer_detail.offer.user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )
        return order

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate(self, data):
        user = self.context['request'].user
        business_user = data.get('business_user')
        if Review.objects.filter(business_user=business_user, reviewer=user).exists():
            raise serializers.ValidationError("Du hast dieses Business bereits bewertet.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return Review.objects.create(reviewer=user, **validated_data)
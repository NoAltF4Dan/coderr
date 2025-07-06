from rest_framework import serializers
from django.db import models
from users.models import CustomUser # Corrected import path for CustomUser
from ..models import Offer, OfferDetail, Order, Review # Existing imports


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(f"/api/offerdetails/{obj.id}/")
        return f"/api/offerdetails/{obj.id}/"


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('price') is not None:
            try:
                ret['price'] = int(float(ret['price']))
            except (ValueError, TypeError):
                pass
        return ret


class OfferRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at",
            "details",
            "min_price", "min_delivery_time",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_min_price(self, obj):
        min_price_value = obj.details.aggregate(models.Min("price"))["price__min"]
        return int(min_price_value) if min_price_value is not None else 0

    def get_min_delivery_time(self, obj):
        min_delivery_time_value = obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]
        return int(min_delivery_time_value) if min_delivery_time_value is not None else 0


class OfferListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at",
            "details",
            "min_price", "min_delivery_time", "user_details"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_min_price(self, obj):
        min_price_value = obj.details.aggregate(models.Min("price"))["price__min"]
        return int(min_price_value) if min_price_value is not None else 0

    def get_min_delivery_time(self, obj):
        min_delivery_time_value = obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]
        return int(min_delivery_time_value) if min_delivery_time_value is not None else 0

    def get_user_details(self, obj):
        return {
            "first_name": obj.user.first_name or "",
            "last_name": obj.user.last_name or "",
            "username": obj.user.username
        }


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "title", "image", "description",
            "details",
            "created_at", "updated_at",
            "min_price", "min_delivery_time", "user_details"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def get_min_price(self, obj):
        min_price_value = obj.details.aggregate(models.Min("price"))["price__min"]
        return int(min_price_value) if min_price_value is not None else 0

    def get_min_delivery_time(self, obj):
        min_delivery_time_value = obj.details.aggregate(models.Min("delivery_time_in_days"))["delivery_time_in_days__min"]
        return int(min_delivery_time_value) if min_delivery_time_value is not None else 0

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
        details_data = validated_data.pop("details", [])
        offer = Offer.objects.create(user=self.context["request"].user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {detail.id: detail for detail in instance.details.all()}

            for detail_data in details_data:
                detail_id = detail_data.get('id')
                if detail_id in existing_details:
                    detail_instance = existing_details[detail_id]
                    for attr, value in detail_data.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    raise serializers.ValidationError(
                        {"details": f"OfferDetail with ID {detail_id} not found or new detail without ID provided for update."}
                    )
        return instance


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True, required=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at", "offer_detail_id"
        ]
        read_only_fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at"
        ]

    def get_price(self, obj):
        return int(obj.price)

    def create(self, validated_data):
        offer_detail_id = validated_data.pop("offer_detail_id", None)
        if not offer_detail_id:
            raise serializers.ValidationError({"offer_detail_id": "This field is required."})

        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError({"offer_detail_id": "OfferDetail does not exist."})

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
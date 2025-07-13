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
        request = self.context.get("request")
        if request and request.method == "PATCH":
            for i, detail in enumerate(value):
                required_fields = ["title", "revisions", "delivery_time_in_days", "price", "features", "offer_type"]
                missing = [field for field in required_fields if field not in detail]
                if missing:
                    raise serializers.ValidationError({
                        f"details[{i}]": [f"Fehlende Felder: {', '.join(missing)}"]
                    })
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
            for i, detail_data in enumerate(details_data):
                offer_type = detail_data.get("offer_type")
                if not offer_type:
                    raise serializers.ValidationError({
                        f"details[{i}]": "Feld 'offer_type' ist erforderlich, um das zugehörige Detail zu finden."
                    })

                try:
                    detail_instance = instance.details.get(offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError({
                        f"details[{i}]": f"Kein OfferDetail mit offer_type '{offer_type}' vorhanden."
                    })

                detail_serializer = OfferDetailSerializer(
                    detail_instance,
                    data=detail_data,
                    context=self.context,
                    partial=False  # ⬅️ erzwingt vollständige Angabe!
                )
                detail_serializer.is_valid(raise_exception=True)
                detail_serializer.save()

        return instance



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request", None)

        # Nur bei PATCH mit Eingabedaten aktivieren
        if request and request.method == "PATCH" and hasattr(self, "initial_data"):
            details_data = self.initial_data.get("details")

            if details_data is not None:
                details_field = self.fields.get("details")
                if details_field and hasattr(details_field, "child"):
                    for child_field in details_field.child.fields.values():
                        child_field.required = True


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
            "created_at", "updated_at"
        ]

    def get_price(self, obj):
        return int(obj.price)
    
    def to_internal_value(self, data):
        allowed = set(self.fields.keys())
        received = set(data.keys())

        unknown = received - allowed
        if unknown:
            raise serializers.ValidationError({
                "non_field_errors": [f"Unerlaubte Felder in Anfrage: {', '.join(unknown)}"]
            })

        return super().to_internal_value(data)
    
    def validate_status(self, value):
        user = self.context['request'].user

        if user.type != "business":
            raise serializers.ValidationError("Nur Business-User dürfen den Status ändern.")

        valid_statuses = [choice[0] for choice in Order._meta.get_field('status').choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Ungültiger Status: '{value}'. Zulässig sind: {', '.join(valid_statuses)}.")

        return value
    
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
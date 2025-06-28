from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.contrib.auth import get_user_model

from ..models import Offer, Order, Review
from .serializers import OfferSerializer, OrderSerializer, ReviewSerializer
from .permissions import (
    IsBusinessUser,
    IsAuthenticatedCustomer,
    IsAuthenticatedBusiness,
    IsReviewOwner,
)

User = get_user_model()

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsBusinessUser]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedCustomer()]
        elif self.action in ["partial_update"]:
            return [IsAuthenticatedBusiness()]
        elif self.action == "destroy":
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )


class OrderCountView(APIView):
    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id, status="in_progress"
        ).count()
        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id, status="completed"
        ).count()
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticatedCustomer()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsReviewOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Review.objects.all()
        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")
        if business_user_id:
            qs = qs.filter(business_user_id=business_user_id)
        if reviewer_id:
            qs = qs.filter(reviewer_id=reviewer_id)
        ordering = self.request.query_params.get("ordering")
        if ordering in ["updated_at", "rating"]:
            qs = qs.order_by(ordering)
        return qs


class BaseInfoView(APIView):
    def get(self, request):
        offer_count = Offer.objects.count()
        order_count = Order.objects.count()
        review_count = Review.objects.count()
        return Response(
            {
                "offer_count": offer_count,
                "order_count": order_count,
                "review_count": review_count,
            }
        )

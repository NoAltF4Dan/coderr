from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg

from users.models import CustomUser
from ..models import OfferDetail, Offer, Order, Review
from .serializers import OfferDetailSerializer, OfferSerializer, OrderSerializer, ReviewSerializer
from .permissions import (
    IsBusinessUser,
    IsAuthenticatedCustomer,
    IsAuthenticatedBusiness,
    IsReviewOwner,
)
from rest_framework.pagination import PageNumberPagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    
User = get_user_model()

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsBusinessUser]
    
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsBusinessUser()]
        return super().get_permissions()

class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.AllowAny]

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
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)



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
    permission_classes = [] 

    def get(self, request):
        review_count = Review.objects.count()

        average_rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        average_rating = round(average_rating, 1)
        business_profile_count = CustomUser.objects.filter(type='business').count()

        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count
        }
        return Response(data)
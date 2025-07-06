from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg

from users.models import CustomUser
from ..models import OfferDetail, Offer, Order, Review
from .serializers import (
    OfferDetailSerializer,
    OfferSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OrderSerializer,
    ReviewSerializer,
)
from .permissions import (
    IsBusinessUser,
    IsAuthenticatedCustomer,
    IsAuthenticatedBusiness,
    IsReviewOwner,
    IsOfferOwner
)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    
User = get_user_model()

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    pagination_class = StandardResultsSetPagination
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'user': ['exact'],
        'details__price': ['gte', 'lte'],
        'details__delivery_time_in_days': ['gte', 'lte'],
    }
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price', 'min_delivery_time']

    def get_serializer_class(self):
        if self.action == 'list':
            return OfferListSerializer
        elif self.action == 'retrieve':
            return OfferRetrieveSerializer
        return OfferSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        elif self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return [IsBusinessUser()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsBusinessUser(), IsOfferOwner()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.distinct()


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None

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
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id, status="in_progress"
        ).count()
        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id, status="completed"
        ).count()
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = None # Removed pagination to return a direct list

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
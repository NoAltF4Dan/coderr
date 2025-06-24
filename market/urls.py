from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BaseInfoView, ReviewViewSet, OfferViewSet, OrderCountView, CompletedOrderCountView

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'reviews', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OfferViewSet

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')

urlpatterns = [
    path('', include(router.urls)),
]

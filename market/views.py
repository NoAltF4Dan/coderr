from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Offer
from .serializers import OfferSerializer
from .permissions import IsBusinessUser 


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsBusinessUser]  

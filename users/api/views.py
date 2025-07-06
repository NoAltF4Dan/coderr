from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from .serializers import BusinessProfileListOutputSerializer, ProfileSerializer, CustomerProfileListSerializer
from authentication.api.permissions import IsOwnerOrReadOnly

from rest_framework.exceptions import PermissionDenied
from .permissions import IsProfileOwner

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

class BusinessProfileListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(type='business')
    serializer_class = BusinessProfileListOutputSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

class CustomerProfileListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(type="customer")
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None




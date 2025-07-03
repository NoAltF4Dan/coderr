from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from .serializers import ProfileSerializer
from authentication.api.permissions import IsOwnerOrReadOnly

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class BusinessProfileListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(type='business')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

class CustomerProfileListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(type='customer')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from .serializers import ProfileSerializer

# 1️⃣ DetailView: GET + PATCH für eigenes Profil
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

# 2️⃣ Liste aller Business-Nutzer
class BusinessProfileListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(type='business')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

# 3️⃣ Liste aller Kunden
class CustomerProfileListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(type='customer')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


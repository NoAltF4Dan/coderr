import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from market.models import Review, Offer
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestBaseInfo:
    def setup_method(self):
        self.client = APIClient()
        self.business = User.objects.create_user(username="biz", password="pass", user_type="business")
        self.customer = User.objects.create_user(username="cust", password="pass", user_type="customer")
        self.business.profile  

        Offer.objects.create(user=self.business, title="Design", description="Desc")
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=4, description="Top")
        Review.objects.create(business_user=self.business, reviewer=self.customer, rating=5, description="Super")

    def test_base_info(self):
        url = reverse("base-info")
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data["review_count"] == 2
        assert response.data["business_profile_count"] >= 1
        assert response.data["offer_count"] == 1
        assert response.data["average_rating"] == 4.5

import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from market.models import Offer, OfferDetail
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestOfferList:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="business1", password="testpass", user_type="business"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_offers_list_empty(self):
        url = reverse("offers-list")  # <-- Wichtig: URL-Namen prüfen!
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_get_offers_list_with_one_offer(self):
        # Erstelle 1 Offer + 3 Details (wie in Doku verlangt)
        offer = Offer.objects.create(
            user=self.user, title="Test Offer", description="Test Desc"
        )
        for i in range(3):
            OfferDetail.objects.create(
                offer=offer,
                title=f"Detail {i}",
                revisions=1,
                delivery_time_in_days=5,
                price=100 + i * 10,
                offer_type="basic",
                features=["Feature1", "Feature2"]
            )

        url = reverse("offers-list")
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Test Offer"
        assert len(response.data["results"][0]["details"]) == 3

def test_create_offer_with_less_than_3_details_returns_400(self):
    url = reverse("offers-list")
    payload = {
        "title": "Zu Wenig Details",
        "description": "Oops",
        "details": [
            {
                "title": "Nur eins",
                "revisions": 1,
                "delivery_time_in_days": 1,
                "price": 10,
                "features": ["Test"],
                "offer_type": "basic"
            }
        ]
    }
    response = self.client.post(url, payload, format="json")
    assert response.status_code == 400
    assert "Ein Offer muss mindestens 3 Details enthalten." in str(response.data)

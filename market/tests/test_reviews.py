import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from market.models import Review
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestReviews:
    def setup_method(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(username="customer", password="pass", user_type="customer")
        self.business = User.objects.create_user(username="business", password="pass", user_type="business")
        self.other = User.objects.create_user(username="other", password="pass", user_type="customer")

    def test_customer_can_create_review(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("reviews-list")
        payload = {
            "business_user": self.business.id,
            "rating": 5,
            "description": "Top!"
        }
        response = self.client.post(url, payload, format="json")
        assert response.status_code == 201

    def test_cannot_create_multiple_reviews_for_same_business(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("reviews-list")
        payload = {"business_user": self.business.id, "rating": 5, "description": "Top!"}
        self.client.post(url, payload, format="json")
        response = self.client.post(url, payload, format="json")
        assert response.status_code == 400

    def test_non_customer_cannot_create_review(self):
        self.client.force_authenticate(user=self.business)
        url = reverse("reviews-list")
        payload = {"business_user": self.business.id, "rating": 5, "description": "Top!"}
        response = self.client.post(url, payload, format="json")
        assert response.status_code == 403

    def test_reviewer_can_update_and_delete(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("reviews-list")
        payload = {"business_user": self.business.id, "rating": 5, "description": "Top!"}
        response = self.client.post(url, payload, format="json")
        review_id = response.data["id"]

        patch_url = reverse("reviews-detail", args=[review_id])
        patch_response = self.client.patch(patch_url, {"rating": 4})
        assert patch_response.status_code == 200

        delete_response = self.client.delete(patch_url)
        assert delete_response.status_code == 204

    def test_non_owner_cannot_update_or_delete(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("reviews-list")
        payload = {"business_user": self.business.id, "rating": 5, "description": "Top!"}
        response = self.client.post(url, payload, format="json")
        review_id = response.data["id"]

        self.client.force_authenticate(user=self.other)
        patch_url = reverse("reviews-detail", args=[review_id])
        patch_response = self.client.patch(patch_url, {"rating": 1})
        assert patch_response.status_code == 403

        delete_response = self.client.delete(patch_url)
        assert delete_response.status_code == 403

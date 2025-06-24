import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from market.models import Offer, OfferDetail, Order
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestOrderList:
    def setup_method(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="customer", password="pass", user_type="customer"
        )
        self.business = User.objects.create_user(
            username="business", password="pass", user_type="business"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass", user_type="customer"
        )

        self.offer = Offer.objects.create(
            user=self.business, title="Design", description="Desc"
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Logo"],
            offer_type="basic"
        )
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type,
        )

    def test_customer_sees_own_orders(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("orders-list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data[0]['id'] == self.order.id

    def test_business_sees_own_orders(self):
        self.client.force_authenticate(user=self.business)
        url = reverse("orders-list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data[0]['id'] == self.order.id

    def test_other_user_sees_no_orders(self):
        self.client.force_authenticate(user=self.other_user)
        url = reverse("orders-list")
        response = self.client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 0
        
@pytest.mark.django_db
class TestOrderCreate:
    def setup_method(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="customer", password="pass", user_type="customer"
        )
        self.business = User.objects.create_user(
            username="business", password="pass", user_type="business"
        )
        self.other_user = User.objects.create_user(
            username="other", password="pass", user_type="business"
        )

        self.offer = Offer.objects.create(
            user=self.business, title="Design", description="Desc"
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Logo"],
            offer_type="basic"
        )

    def test_customer_can_create_order(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("orders-list")
        payload = {"offer_detail_id": self.detail.id}
        response = self.client.post(url, payload, format="json")
        assert response.status_code == 201
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.customer_user == self.customer
        assert order.business_user == self.business

    def test_non_customer_cannot_create_order(self):
        self.client.force_authenticate(user=self.other_user)  # ist Business
        url = reverse("orders-list")
        payload = {"offer_detail_id": self.detail.id}
        response = self.client.post(url, payload, format="json")
        assert response.status_code == 403

@pytest.mark.django_db
class TestOrderPatch:
    def setup_method(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="customer", password="pass", user_type="customer"
        )
        self.business = User.objects.create_user(
            username="business", password="pass", user_type="business"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="pass"
        )

        self.offer = Offer.objects.create(
            user=self.business, title="Design", description="Desc"
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Logo"],
            offer_type="basic"
        )
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type,
        )

    def test_business_can_patch_status(self):
        self.client.force_authenticate(user=self.business)
        url = reverse("orders-detail", args=[self.order.id])
        payload = {"status": "completed"}
        response = self.client.patch(url, payload, format="json")
        assert response.status_code == 200
        self.order.refresh_from_db()
        assert self.order.status == "completed"

    def test_customer_cannot_patch_status(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse("orders-detail", args=[self.order.id])
        payload = {"status": "completed"}
        response = self.client.patch(url, payload, format="json")
        assert response.status_code == 403

@pytest.mark.django_db
class TestOrderDelete:
    def setup_method(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(
            username="customer", password="pass", user_type="customer"
        )
        self.business = User.objects.create_user(
            username="business", password="pass", user_type="business"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="pass"
        )

        self.offer = Offer.objects.create(
            user=self.business, title="Design", description="Desc"
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Logo"],
            offer_type="basic"
        )
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type,
        )

    def test_admin_can_delete_order(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse("orders-detail", args=[self.order.id])
        response = self.client.delete(url)
        assert response.status_code == 204
        assert Order.objects.count() == 0

    def test_non_admin_cannot_delete_order(self):
        self.client.force_authenticate(user=self.business)
        url = reverse("orders-detail", args=[self.order.id])
        response = self.client.delete(url)
        assert response.status_code == 403

@pytest.mark.django_db
class TestOrderCounts:
    def setup_method(self):
        self.client = APIClient()
        self.business = User.objects.create_user(username="business", password="pass", user_type="business")
        self.customer = User.objects.create_user(username="customer", password="pass", user_type="customer")

        self.offer = Offer.objects.create(user=self.business, title="Design", description="Desc")
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic",
            revisions=1,
            delivery_time_in_days=5,
            price=100,
            features=["Logo"],
            offer_type="basic"
        )

        # 2 laufende Orders
        for _ in range(2):
            Order.objects.create(
                customer_user=self.customer,
                business_user=self.business,
                offer_detail=self.detail,
                title=self.detail.title,
                revisions=self.detail.revisions,
                delivery_time_in_days=self.detail.delivery_time_in_days,
                price=self.detail.price,
                features=self.detail.features,
                offer_type=self.detail.offer_type,
                status="in_progress"
            )
        # 1 abgeschlossene Order
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
            offer_type=self.detail.offer_type,
            status="completed"
        )

    def test_order_count(self):
        url = reverse("order-count", args=[self.business.id])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data["order_count"] == 2

    def test_completed_order_count(self):
        url = reverse("completed-order-count", args=[self.business.id])
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.data["completed_order_count"] == 1

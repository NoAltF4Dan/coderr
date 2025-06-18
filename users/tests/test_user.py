import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import CustomUser

pytestmark = pytest.mark.django_db

def create_user(**params):
    return CustomUser.objects.create_user(**params)

def get_token(client, email, password):
    response = client.post('/api/login/', {
        "username": email,
        "password": password
    })
    return response.data['token']

def test_retrieve_profile():
    client = APIClient()
    user = create_user(username='foo@bar.com', email='foo@bar.com', password='secret')
    token = get_token(client, 'foo@bar.com', 'secret')

    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    response = client.get(f'/api/profile/{user.pk}/')

    assert response.status_code == 200
    assert response.data['username'] == 'foo@bar.com'
    # Felder nie null
    assert response.data['first_name'] == ''

def test_update_own_profile():
    client = APIClient()
    user = create_user(username='foo@bar.com', email='foo@bar.com', password='secret')
    token = get_token(client, 'foo@bar.com', 'secret')

    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    payload = {
        "first_name": "John",
        "last_name": "Doe"
    }
    response = client.patch(f'/api/profile/{user.pk}/', payload)

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "John"

def test_cannot_update_others_profile():
    client = APIClient()
    user1 = create_user(username='foo@bar.com', email='foo@bar.com', password='secret')
    user2 = create_user(username='other@bar.com', email='other@bar.com', password='secret')

    token = get_token(client, 'foo@bar.com', 'secret')
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    payload = {
        "first_name": "Hacker"
    }
    response = client.patch(f'/api/profile/{user2.pk}/', payload)

    assert response.status_code == 403

def test_list_business_profiles():
    client = APIClient()
    create_user(username='biz1@biz.com', email='biz1@biz.com', password='secret', type='business')
    create_user(username='cust1@cust.com', email='cust1@cust.com', password='secret', type='customer')

    user = create_user(username='foo@bar.com', email='foo@bar.com', password='secret')
    token = get_token(client, 'foo@bar.com', 'secret')
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    response = client.get('/api/profile/business/')
    assert response.status_code == 200
    assert all(u['type'] == 'business' for u in response.data)

def test_list_customer_profiles():
    client = APIClient()
    create_user(username='biz1@biz.com', email='biz1@biz.com', password='secret', type='business')
    create_user(username='cust1@cust.com', email='cust1@cust.com', password='secret', type='customer')

    user = create_user(username='foo@bar.com', email='foo@bar.com', password='secret')
    token = get_token(client, 'foo@bar.com', 'secret')
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    response = client.get('/api/profile/customer/')
    assert response.status_code == 200
    assert all(u['type'] == 'customer' for u in response.data)

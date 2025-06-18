# authentication/tests/test_api.py

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from users.models import CustomUser


class RegistrationTests(APITestCase):

    def test_registration_success(self):
        """
        Test: Erfolgreiche Registrierung eines neuen Benutzers.
        Erwartung laut Doku:
        - Status 201
        - Antwort enthält Token, username, email, user_id
        """
        url = reverse('registration')  # URL-Name aus authentication.api.urls
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertIn('user_id', response.data)

    def test_registration_password_mismatch(self):
        """
        Test: Registrierung schlägt fehl, wenn Passwörter nicht übereinstimmen.
        Erwartung laut Doku:
        - Status 400
        """
        url = reverse('registration')
        data = {
            "username": "testuser",
            "email": "test@mail.de",
            "password": "password1",
            "repeated_password": "password2",
            "type": "customer"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """
    Testklasse für den Login (/api/login/)
    """

    def setUp(self):
        """
        Vor jedem Test: einen User anlegen, der sich einloggen kann.
        """
        self.user = CustomUser.objects.create_user(
            username="loginuser",
            email="login@mail.de",
            password="loginPassword",
            type="customer"
        )

    def test_login_success(self):
        """
        Test: Erfolgreicher Login.
        Erwartung laut Doku:
        - Status 200
        - Antwort enthält Token, username, email, user_id
        """
        url = reverse('login')
        data = {
            "username": "loginuser",
            "password": "loginPassword"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIn('user_id', response.data)

    def test_login_wrong_password(self):
        """
        Test: Login schlägt fehl mit falschem Passwort.
        Erwartung laut Doku:
        - Status 400
        """
        url = reverse('login')
        data = {
            "username": "loginuser",
            "password": "wrongPassword"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

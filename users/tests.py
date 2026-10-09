from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, VerificationRequest
from business.models import Business


class AuthenticationRegressionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='explorer', email='test@example.com', password='ExampleStrongPass123!')

    def test_rotated_refresh_token_cannot_be_reused(self):
        refresh = str(RefreshToken.for_user(self.user))
        first = self.client.post('/api/auth/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(first.status_code, 200)
        self.assertIn('refresh', first.data)
        second = self.client.post('/api/auth/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(second.status_code, 401)

    def test_duplicate_email_case_is_rejected(self):
        response = self.client.post('/api/auth/register/', {'username': 'new', 'email': 'TEST@example.com', 'password': 'OtherStrongPass123!'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_approval_cannot_create_business_twice(self):
        admin = User.objects.create_user(username='admin', rol='admin')
        verification = VerificationRequest.objects.create(user=self.user, business_name='Shop', business_address='Address', id_card_number='123', identity_document='document.jpg')
        self.client.force_authenticate(admin)
        url = f'/api/auth/verification-requests/{verification.pk}/approve/'
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 400)
        self.assertEqual(Business.objects.filter(owner=self.user).count(), 1)

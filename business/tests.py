from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from gastronomy.models import Department, TraditionalFood
from .models import Business, BusinessMenuItem, BusinessQualification, Menu


class BusinessAPIRegressionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username='owner', rol='owner')
        self.other = User.objects.create_user(username='other', rol='owner')
        self.visitor = User.objects.create_user(username='visitor')
        self.business = Business.objects.create(name='Local', address='Address', owner=self.owner)
        self.other_business = Business.objects.create(name='Other', address='Address', owner=self.other)
        self.item = BusinessMenuItem.objects.create(name='Dish', business=self.business, price=10)
        self.menu = Menu.objects.create(business=self.business, menu_item=self.item, price=10)
        self.review = BusinessQualification.objects.create(user=self.visitor, business=self.business, qualification=5, evidence_image='evidence.jpg')

    def test_owner_cannot_delete_another_menu_using_filter(self):
        self.client.force_authenticate(self.other)
        response = self.client.delete(f'/api/business/menus/{self.menu.pk}/?business={self.business.pk}')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Menu.objects.filter(pk=self.menu.pk).exists())

    def test_user_and_business_owner_cannot_delete_another_review(self):
        for user in (self.other, self.owner):
            self.client.force_authenticate(user)
            response = self.client.delete(f'/api/business/qualifications/{self.review.pk}/?business={self.business.pk}')
            self.assertEqual(response.status_code, 404)
        self.assertTrue(BusinessQualification.objects.filter(pk=self.review.pk).exists())

    def test_review_author_can_delete(self):
        self.client.force_authenticate(self.visitor)
        self.assertEqual(self.client.delete(f'/api/business/qualifications/{self.review.pk}/').status_code, 204)

    def test_menu_item_contract_and_price_sync(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post('/api/business/menu-items/', {'name': 'New', 'business': self.business.pk, 'price': '25.50'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['price'], '25.50')
        item = BusinessMenuItem.objects.get(pk=response.data['id'])
        self.assertEqual(Menu.objects.get(menu_item=item).price, Decimal('25.50'))
        response = self.client.get('/api/business/menu-items/')
        self.assertEqual(response.status_code, 200)

    def test_cannot_move_item_to_another_owners_business(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(f'/api/business/menu-items/{self.item.pk}/', {'business': self.other_business.pk}, format='json')
        self.assertEqual(response.status_code, 400)
        self.item.refresh_from_db()
        self.assertEqual(self.item.business_id, self.business.pk)

    def test_menu_rejects_mismatched_business_and_item(self):
        self.client.force_authenticate(self.other)
        response = self.client.post('/api/business/menus/', {'business': self.other_business.pk, 'menu_item': self.item.pk, 'price': '10'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_menu_price_update_syncs_item(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(f'/api/business/menus/{self.menu.pk}/', {'price': '30'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.item.refresh_from_db()
        self.assertEqual(self.item.price, Decimal('30'))

    def test_complete_profile_validates_coordinates_and_phone(self):
        self.client.force_authenticate(self.owner)
        for payload in ({'latitude': 'invalid'}, {'contact_number': 'abc'}):
            response = self.client.patch(f'/api/business/business/{self.business.pk}/complete_profile/', payload, format='json')
            self.assertEqual(response.status_code, 400)

    def test_only_admin_can_mark_validated_variant(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(f'/api/business/menu-items/{self.item.pk}/', {'is_traditional_variant': True}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_admin_validation_rejects_missing_food(self):
        admin = User.objects.create_user(username='admin', rol='admin')
        self.client.force_authenticate(admin)
        response = self.client.patch(f'/api/business/menu-items/{self.item.pk}/validate_for_album/', {'traditional_food': 999}, format='json')
        self.assertEqual(response.status_code, 400)
        self.item.refresh_from_db()
        self.assertFalse(self.item.is_traditional_variant)

    def test_duplicate_review_returns_validation_error(self):
        from .serializers import BusinessQualificationSerializer
        from types import SimpleNamespace
        serializer = BusinessQualificationSerializer(context={'request': SimpleNamespace(user=self.visitor)})
        from rest_framework.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            serializer.validate({'business': self.business})

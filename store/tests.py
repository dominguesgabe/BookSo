from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from store.models import Product
from tests.factories import product_factory


class ProductTestCase(TestCase):
    def setUp(self):
        product_factory()

    def test_check_if_book_exists(self):
        product = Product.objects.all().first()

        self.assertIsInstance(product, Product)


class ProductAPITestCase(APITestCase):
    def setUp(self):
        product_factory()

    def test_api_get_products(self):
        url = reverse("product-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

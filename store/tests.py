from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from book.models import Book
from store.models import Product
from store.serializers import ProductSerializer
from tests.factories import book_factory, product_factory


class ProductAPITestCase(APITestCase):
    def setUp(self):
        book = book_factory()
        product_factory(book)

        # mocking authentication
        self.user = User.objects.create(
            username="jobert_silverado", password="supersecret", is_staff=True
        )
        self.token = str(AccessToken.for_user(self.user))

    def inject_credentials(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    # GET product list
    def test_api_get_products(self):
        url = reverse("product-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    # GET product detail
    def test_api_get_product(self):
        db_product = Product.objects.all().first()
        assert db_product is not None

        url = reverse("product-detail", kwargs={"pk": db_product.id})
        response = self.client.get(url)

        expected = ProductSerializer(db_product).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    # POST product should succeed because there is a logged staff user
    def test_api_create_product_success(self):
        book = Book.objects.all().first()
        assert book is not None

        url = reverse("product-list")
        payload = {
            "available_quantity": 3,
            "price": 12,
            "product_type": Product.DIGITAL,
            "book_id": book.id,
        }
        self.inject_credentials()
        response = self.client.post(url, payload)

        created_product = Product.objects.all().last()
        expected = ProductSerializer(created_product).data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected)

    # POST product should fail because user is not authenticated
    def test_api_create_product_unauthenticated(self):
        book = Book.objects.all().first()
        assert book is not None

        url = reverse("product-list")
        payload = {
            "available_quantity": 3,
            "price": 12,
            "product_type": Product.DIGITAL,
            "book_id": book.id,
        }

        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # POST product should fail because already has a product associated with same book and product_type
    def test_api_create_product_existent_product_type(self):
        book = Book.objects.all().first()
        assert book is not None

        url = reverse("product-list")

        payload = {
            "available_quantity": 1,
            "price": 20.5,
            "product_type": Product.PHYSICAL,
            "book_id": book.id,
        }

        self.inject_credentials()
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["product_type"],
            ["Já existe um produto associado ao livro com o mesmo tipo."],
        )

    # PATCH product should succeed
    def test_api_update_product_success(self):
        product = Product.objects.all().first()
        assert product is not None

        self.assertEqual(product.available_quantity, 10)
        self.assertEqual(product.price, 10.5)

        url = reverse("product-detail", args=[product.id])
        self.inject_credentials()
        response = self.client.patch(url, {"available_quantity": 8, "price": 14.99})

        updated_product = Product.objects.all().first()
        assert updated_product is not None

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_product.available_quantity, 8)
        self.assertEqual(updated_product.price, 14.99)

    # PATCH product should fail because already exists a product with same book and product_type
    def test_api_update_product_fail_product_type(self):
        book = Book.objects.all().first()
        product = product_factory(book, product_type=Product.DIGITAL)
        assert book is not None

        self.assertEqual(product.product_type, Product.DIGITAL)

        url = reverse("product-detail", kwargs={"pk": product.id})
        self.inject_credentials()
        response = self.client.patch(url, {"product_type": Product.PHYSICAL})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["product_type"],
            ["Já existe um produto associado ao livro com o mesmo tipo."],
        )

    # DELETE product should succeed
    def test_api_delete_product_success(self):
        product = Product.objects.all().first()
        assert product is not None

        url = reverse("product-detail", kwargs={"pk": product.id})
        self.inject_credentials()
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # DELETE product should fail because user is not authenticated
    def test_api_delete_product_unauthenticated_fail(self):
        product = Product.objects.all().first()
        assert product is not None

        url = reverse("product-detail", kwargs={"pk": product.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

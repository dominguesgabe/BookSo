from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from book.models import Book
from store.models import Product, Cart
from store.serializers import ProductSerializer, CartSerializer
from tests.factories import (
    book_factory,
    product_factory,
    cart_item_factory,
    cart_factory,
    customer_factory,
)


class ProductAPITestCase(APITestCase):
    def setUp(self):
        book = book_factory()
        product_factory(book=book)

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
        product = product_factory(book=book, product_type=Product.DIGITAL)
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


class CartAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="jobert_silverado", password="supersecret", is_staff=True
        )
        self.token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        customer_factory(user=self.user)
        self.cart_add_url = reverse("cart-add")

    # GET logged customer cart
    def test_api_get_cart(self):
        url = reverse("cart-list")
        response = self.client.get(url)

        cart = Cart.objects.first()
        expected_cart_sereializer = CartSerializer(cart)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_cart_sereializer.data)

    # POST customer cart add product
    def test_api_post_product_to_cart(self):
        book = book_factory()
        product = product_factory(book=book)

        response = self.client.post(
            self.cart_add_url, {"product_id": product.id, "quantity": 1}
        )

        serialized_response = CartSerializer(data=response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(serialized_response.is_valid())

    # POST customer cart add product with invalid body
    def test_api_post_product_to_cart_invalid_body(self):
        book = book_factory()
        product = product_factory(book=book)

        response = self.client.post(
            self.cart_add_url, {"produ_id": product.id, "quantity": True}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # POST customer cart add product, should not succeed
    def test_api_post_product_unavailable_quantity(self):
        book = book_factory()
        product = product_factory(book=book, available_quantity=1)

        response = self.client.post(
            self.cart_add_url, {"product_id": product.id, "quantity": 2}
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["quantity"],
            [
                f"A quantidade solicitada é maior que o estoque disponível para o produto {book.name}."
            ],
        )

    # POST customer cart add product not found, should not succeed
    def test_api_post_product_not_found(self):
        response = self.client.post(
            self.cart_add_url, {"product_id": 555, "quantity": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # POST customer cart add product not found, should not succeed
    def test_api_post_product_not_active(self):
        book = book_factory()
        product = product_factory(book=book, available_quantity=1, active=False)

        response = self.client.post(
            self.cart_add_url, {"product_id": product.id, "quantity": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["active"],
            ["O produto desejado não está ativo."],
        )

    # POST customer cart add product digital when already has the same book but different type
    def test_api_post_product_with_different_type(self):
        book = book_factory()
        digital_product = product_factory(
            book=book, available_quantity=1, product_type=Product.DIGITAL
        )
        physical_product = product_factory(
            book=book, available_quantity=1, product_type=Product.PHYSICAL
        )

        digital_product_response = self.client.post(
            self.cart_add_url, {"product_id": digital_product.id, "quantity": 1}
        )
        physical_product_response = self.client.post(
            self.cart_add_url, {"product_id": physical_product.id, "quantity": 1}
        )

        self.assertEqual(digital_product_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(physical_product_response.status_code, status.HTTP_201_CREATED)

    # POST customer cart add product physical to a cart that already have it
    def test_api_post_product_with_same_type(self):
        book = book_factory()
        physical_product = product_factory(
            book=book, available_quantity=2, product_type=Product.PHYSICAL
        )

        first_response = self.client.post(
            self.cart_add_url, {"product_id": physical_product.id, "quantity": 1}
        )
        second_response = self.client.post(
            self.cart_add_url, {"product_id": physical_product.id, "quantity": 1}
        )

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)

    # POST customer cart add product physical to a cart that already have it but exceed available quantity
    def test_api_post_product_with_same_type_exceed_available(self):
        book = book_factory()
        physical_product = product_factory(
            book=book, available_quantity=2, product_type=Product.PHYSICAL
        )

        response = self.client.post(
            self.cart_add_url, {"product_id": physical_product.id, "quantity": 10}
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            response.data["quantity"],
            [
                f"A quantidade solicitada é maior que o estoque disponível para o produto {book.name}."
            ],
        )

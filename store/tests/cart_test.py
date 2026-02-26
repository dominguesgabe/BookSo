from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from store.models import Product, Cart
from store.serializers import CartSerializer
from tests.factories import (
    book_factory,
    product_factory,
    customer_factory,
)


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


# fazer um teste e verificar que ele chama a api externa
# criar mock
# apliccar o mock no teste
# verificar que a api não é mais chamada

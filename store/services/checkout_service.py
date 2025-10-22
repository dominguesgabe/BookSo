from decouple import config
from typing import cast
import stripe
from store.models import Cart, Order, Customer, Product
from store.serializers import (
    CartSerializer,
    ProductSerializer,
    ExternalProductSerializer,
)
from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

stripe.api_key = config("STRIPE_API_SECRET_KEY")


def checkout_create(user: User):
    # ao criar um product aqui tem que criar na stripe também
    # pegar o carrinho
    customer = get_object_or_404(Customer, user=user)

    cart = (
        Cart.objects.filter(customer=customer)
        .exclude(checked_out_at__isnull=False)
        .last()
    )

    if not cart:
        return Response({"cart": ["Carrinho não encontrado."]})

    # criar order

    cart_items = CartSerializer(cart).data["items"]

    total_price = sum(
        float(cart_item["price"]) * cart_item["quantity"] for cart_item in cart_items
    )

    order = (
        Order.objects.filter(cart=cart)
        .order_by("-created_at")
        .exclude(status="success")
        .first()
    )

    if not order:
        order = Order.objects.create(cart=cart, total_price=total_price)

    # criar os itens no stripe caso eles não existam
    # criar a sessão
    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {"price": "price_1SFh1QFCQyfyO65gpohaW2H4", "quantity": 1}
            ],  # replace with product
            mode="payment",
            success_url="http://localhost:8000/success.html",  # success endpoint
            cancel_url="http://localhost:8000/success.html",  # error endpoint
        )
    except Exception:
        return Response(
            {"order": ["Erro desconhecido ao criar pedido."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"session_url": session.url}, status=status.HTTP_200_OK)


def create_product_on_checkout_platform(serializer: ProductSerializer) -> str:
    serialized_external_product = _external_product_data_factory(serializer)

    product = stripe.Product.create(**serialized_external_product.validated_data)

    external_id = cast("str", product.default_price)

    return external_id


def update_product_on_checkout_platform(serializer: ProductSerializer):
    serialized_external_product = _external_product_data_factory(serializer)

    product_id = serialized_external_product.pop("id")

    stripe.Product.modify(product_id, **serialized_external_product)


def _external_product_data_factory(
    serializer: ProductSerializer,
):
    data = {
        "id": serializer.data["id"],
        "name": serializer.data["book"]["name"],
        "shippable": serializer.data["product_type"] == Product.PHYSICAL,
        "default_price_data": {"unit_amount_decimal": serializer.data["price"] * 100},
    }

    serialized_external_product = ExternalProductSerializer(data=data)
    serialized_external_product.is_valid(raise_exception=True)

    return serialized_external_product.validated_data

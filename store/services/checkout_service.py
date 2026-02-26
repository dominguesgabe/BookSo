from decouple import config
from typing import Any
import stripe
from store.models import Cart, Order, Customer, Product
from store.serializers import (
    CartSerializer,
    ProductSerializer,
    ExternalProductSerializer,
    DefaultPriceSerializer,
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
    data = {
        "id": serializer.data["id"],
        "name": serializer.data["book"]["name"],
        "shippable": serializer.data["product_type"] == Product.PHYSICAL,
        "default_price_data": {"unit_amount_decimal": serializer.data["price"] * 100},
    }

    serialized_external_product = ExternalProductSerializer(data=data)
    serialized_external_product.is_valid(raise_exception=True)

    product = stripe.Product.create(**serialized_external_product.validated_data)

    # frankenstein monster
    assert product.default_price is not None
    external_price_id = (
        product.default_price.id
        if isinstance(product.default_price, stripe.Price)
        else product.default_price
    )

    return external_price_id


def update_product_on_checkout_platform(
    product_serializer: ProductSerializer, request_data: dict[str, Any]
):
    product_id = str(product_serializer.data["id"])
    data = {}

    if id := request_data.get("id"):
        data["id"] = id

    if name := request_data.get("name"):
        data["name"] = name

    if product_type := request_data.get("product_type"):
        data["shippable"] = product_type == Product.PHYSICAL

    if price := request_data.get("price"):
        # I was not able to update the existing price, TODO: try again
        new_external_price = stripe.Price.create(
            currency="brl",
            unit_amount_decimal=str(price * 100),
            product=product_id,
        )
        data["default_price"] = new_external_price.id

    stripe.Product.modify(product_id, **data)

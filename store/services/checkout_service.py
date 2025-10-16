from decouple import config
import stripe
from store.models import Cart, Order, Customer, CartItem
from store.serializers import CartSerializer
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
    # try:
    #     session = stripe.checkout.Session.create(
    #         line_items=[
    #             {"price": "price_1SFh1QFCQyfyO65gpohaW2H4", "quantity": 1}
    #         ],  # replace with product
    #         mode="payment",
    #         success_url="http://localhost:8000/success.html",  # success endpoint
    #         cancel_url="http://localhost:8000/success.html",  # error endpoint
    #     )
    # except Exception:
    #     return Response(
    #         {"order": ["Erro desconhecido ao criar pedido."]},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    return Response({"session_url": "session.url"}, status=status.HTTP_200_OK)

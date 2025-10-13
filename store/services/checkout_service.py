from decouple import config
import stripe
from store.models import Cart, Order
from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404

stripe.api_key = config("STRIPE_API_SECRET_KEY")


def checkout(user: User):
    # pegar o carrinho
    cart = get_object_or_404(Cart, user=user)
    # cart_items = cart
    # criar order
    order = Order.objects.create(
        cart=cart,
    )
    # criar os itens lá caso eles não existam
    # criar a sessão
    try:
        session = stripe.checkout.Session.create(
            line_items=[{"price": "price_1SFh1QFCQyfyO65gpohaW2H4", "quantity": 1}],
            mode="payment",
            success_url="http://localhost:8000/success.html",  # success endpoint
            cancel_url="http://localhost:8000/success.html",  # error endpoint
        )

    except Exception as e:
        return e

    return session

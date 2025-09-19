from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.response import Response
from store.models import Cart, Product, Customer, CartItem
from django.contrib.auth.models import User
from store.serializers import AddToCartSerializer
from rest_framework import status
from rest_framework.generics import get_object_or_404


def add_to_cart(user: User, serializer: AddToCartSerializer):
    # validate if product can be added or early return
    # if product already on cart and phsysical add 1
    # get or create cart
    # create cartItem
    # add cartItem to cart
    customer = get_object_or_404(Customer, user=user)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    requested_quantity = serializer.validated_data["quantity"]
    product = get_object_or_404(Product, pk=serializer.validated_data["product_id"])

    if not product.active:
        return Response(
            {"active": ["O produto desejado não está ativo."]},
            status=status.HTTP_404_NOT_FOUND,
        )

    if (
        requested_quantity > product.available_quantity
        and product.product_type == Product.PHYSICAL
    ):
        return Response(
            {
                "quantity": [
                    f"A quantidade solicitada é maior que o estoque disponível para o produto {product.book.name}."
                ]
            },
            status=status.HTTP_409_CONFLICT,
        )

    cart, created = Cart.objects.get_or_create(customer=customer)

    # create cartitem

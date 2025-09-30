from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from store.models import Cart, CartItem, Customer, Product
from store.serializers import AddToCartSerializer, CartItemSerializer


def add_to_cart(user: User, serializer: AddToCartSerializer) -> Response:
    customer = get_object_or_404(Customer, user=user)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    product = get_object_or_404(Product, pk=serializer.validated_data["product_id"])

    if not product.active:
        return Response(
            {"active": ["O produto desejado não está ativo."]},
            status=status.HTTP_404_NOT_FOUND,
        )

    requested_quantity = serializer.validated_data["quantity"]

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

    cart, _ = Cart.objects.get_or_create(customer=customer)

    cart_item, is_new_cart_item = CartItem.objects.get_or_create(
        cart=cart, product=product
    )

    if not is_new_cart_item and product.product_type == Product.PHYSICAL:
        new_quantity = cart_item.quantity + requested_quantity

        if new_quantity > product.available_quantity:
            return Response(
                {
                    "quantity": [
                        f"A quantidade solicitada é maior que o estoque disponível para o produto {product.book.name}."
                    ]
                },
                status=status.HTTP_409_CONFLICT,
            )

        cart_item.quantity = new_quantity
    else:
        cart_item.quantity = 1

    cart_item.cart = cart
    cart_item.product = product
    cart_item.price = product.price

    cart_item.save()

    return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

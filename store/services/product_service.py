import logging
from typing import Any

from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from store.serializers import ProductSerializer
from store.models import Product
from store.services import checkout_service
import stripe

logger = logging.getLogger()


def create_product(*, payload: dict[str, Any]):
    serializer = ProductSerializer(data=payload)
    serializer.is_valid(raise_exception=True)

    db_book = serializer.validated_data["book"]

    db_product = Product.objects.filter(
        book=db_book, product_type=serializer.validated_data["product_type"]
    ).exists()

    if db_product:
        logger.info(
            "Product associated to the same book with same type exist on the database"
        )
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={
                "product_type": [
                    "Já existe um produto associado ao livro com o mesmo tipo."
                ]
            },
        )

    save_kwargs: dict[str, Any] = {}
    if serializer.validated_data["product_type"] == Product.DIGITAL:
        save_kwargs["available_quantity"] = 1

    product = serializer.save(**save_kwargs)

    # shouldn't this block wrap everything?
    try:
        external_price_id = checkout_service.create_product_on_checkout_platform(
            serializer=serializer
        )

        product.external_price_id = external_price_id
        product.save()

    except stripe.InvalidRequestError:
        return Response(
            {
                "external_product": [
                    "Não foi possível criar o produto na plataforma de pagamentos."
                ]
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


def update_product(self, request, *args, **kwargs):
    partial = kwargs.pop("partial", False)
    instance: Product = self.get_object()
    serializer: ProductSerializer = self.get_serializer(
        instance, data=request.data, partial=partial
    )
    serializer.is_valid(raise_exception=True)

    if product_type := serializer.validated_data.get("product_type"):
        db_product = (
            Product.objects.filter(
                book=instance.book,
                product_type=product_type,
            )
            .exclude(id=instance.id)
            .first()
        )

        if db_product:
            logger.info("Found product with same book and type.")
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "product_type": [
                        "Já existe um produto associado ao livro com o mesmo tipo."
                    ]
                },
            )

    # shouldnt this block wrap everything?
    try:
        self.perform_update(serializer)

        request_data = request.data
        checkout_service.update_product_on_checkout_platform(serializer, request_data)
    except ValidationError as error:
        return Response(
            {"external_product": error.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except stripe.InvalidRequestError as error:
        return Response(
            {"external_product": error._message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(serializer.data, status=status.HTTP_200_OK)

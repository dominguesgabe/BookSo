from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status
from store.models import Cart, Customer, Product
from store.permissions import IsOwner
from store.serializers import CartSerializer, CustomerSerializer, ProductSerializer
from rest_framework.response import Response
import logging

logger = logging.getLogger()


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()

    serializer_class = CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
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

        save_kwargs = {}
        if serializer.validated_data["product_type"] == "ebook":
            save_kwargs["available_quantity"] = 1

        product = serializer.save(**save_kwargs)
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance: Product = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("product_type"):
            db_product = (
                Product.objects.filter(
                    book=instance.book,
                    product_type=serializer.validated_data["product_type"],
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

        self.perform_update(serializer)

        return Response(serializer.data)

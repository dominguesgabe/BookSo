from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets, status, mixins
from rest_framework import permissions as rest_permissions
from rest_framework.decorators import action
from store.models import Cart, Customer, Product
from store.services import add_to_cart
from permissions import permissions
from store.serializers import (
    CartSerializer,
    CustomerSerializer,
    ProductSerializer,
    AddToCartSerializer,
    UserSerializer,
)
from rest_framework.response import Response
import logging

logger = logging.getLogger()


class CartViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    # queryset = Cart.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsOwnerOrAdminUser]

    @action(detail=False, methods=["POST"], url_path="add")
    def add_item(self, request):
        if not request.user:
            Response(
                {
                    "user": [
                        "Você precisa estar logado para realizar esta ação. Faça login ou crie sua conta!"
                    ]
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        add_to_cart_serializer = AddToCartSerializer(data=request.data)

        response = add_to_cart(user=request.user, serializer=add_to_cart_serializer)

        # improve response
        # add test cases
        return response

    # this is not a real list, I want to have the user cart on this route
    def list(self, request, *args, **kwargs):
        user = request.user
        customer, _ = Customer.objects.get_or_create(user=user)
        cart, _ = Cart.objects.get_or_create(customer=customer)

        cart_data = CartSerializer(cart).data

        return Response(cart_data, status=status.HTTP_200_OK)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [rest_permissions.IsAdminUser]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUserOrViewOnly]

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
        if serializer.validated_data["product_type"] == Product.DIGITAL:
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

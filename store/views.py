import logging

from rest_framework import mixins, status, viewsets
from rest_framework import permissions as rest_permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from permissions import permissions
from store.models import Cart, Customer, Product
from store.serializers import (
    AddToCartSerializer,
    CartSerializer,
    CustomerSerializer,
    ProductSerializer,
)
from store.services import cart_service, checkout_service, product_service

logger = logging.getLogger()


class CartViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsOwnerOrAdminUser]

    @action(detail=False, methods=["POST"], url_path="add")
    def add(self, request):
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

        response = cart_service.add_to_cart(
            user=request.user, serializer=add_to_cart_serializer
        )

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
        response = product_service.create_product(payload=request.data)
        return response

    def update(self, request, *args, **kwargs):
        response = product_service.update_product(self, request, *args, **kwargs)
        return response


class CheckoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsOwnerOrAdminUser]

    def create(self, request):
        checkout_session = checkout_service.checkout_create(user=request.user)
        return checkout_session

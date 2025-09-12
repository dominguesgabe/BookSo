from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from store.models import Cart, Customer
from store.permissions import IsOwner
from store.serializers import CartSerializer, CustomerSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    authentication_classes = [JWTAuthentication]

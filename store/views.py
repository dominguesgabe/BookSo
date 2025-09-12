from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from store.models import Cart
from store.permissions import IsOwner
from store.serializers import CartSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwner]

    # só o próprio dono deve poder ver e alterar seu carrinho

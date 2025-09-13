from rest_framework.decorators import (
    api_view,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_simplejwt.authentication import JWTAuthentication


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
def api_root(request, format=None):
    return Response(
        {
            "books": reverse("book-list", request=request, format=format),
            "genres": reverse("genre-list", request=request, format=format),
            "cart": reverse("cart-list", request=request, format=format),
            "customers": reverse("customer-list", request=request, format=format),
            "products": reverse("product-list", request=request, format=format),
        }
    )

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from book.views import BookViewSet, GenreViewSet
from store import views
from bff.views import api_root

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"books", BookViewSet, basename="book")
router.register(r"cart", views.CartViewSet, basename="cart")
router.register(r"customers", views.CustomerViewSet, basename="customer")
router.register(r"products", views.ProductViewSet, basename="product")
router.register(r"checkout", views.CheckoutViewSet, basename="checkout")


urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("bff/", api_root, name="api_root"),
    path("bff/", include(router.urls)),
]

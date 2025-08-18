from django.urls import path, include
from rest_framework.routers import DefaultRouter
from book import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r"books", views.BookViewSet, basename="book")
router.register(r"genres", views.GenreViewSet, basename="genre")

urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("bff/", include(router.urls)),
]

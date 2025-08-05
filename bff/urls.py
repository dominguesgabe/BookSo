from django.urls import path, include
from rest_framework.routers import DefaultRouter
from book import views

router = DefaultRouter()
router.register(r"genres", views.GenreViewSet, basename="genre")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls")),
]

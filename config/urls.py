from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("bff.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("rest_framework.urls")),
]

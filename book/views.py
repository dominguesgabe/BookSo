from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from book.models import Genre
from book.serializers import GenreSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

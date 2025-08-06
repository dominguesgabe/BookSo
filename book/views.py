from rest_framework import viewsets, permissions
from book.models import Genre
from book.serializers import GenreSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # permission_classes = [permissions.IsAuthenticated]

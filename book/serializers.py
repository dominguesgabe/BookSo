from rest_framework import serializers
from book.models import Book, Genre


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Genre
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    queryset = Book.objects.all()

    name = serializers.CharField()
    language = serializers.CharField()
    publish_date = serializers.DateField()
    page_number = serializers.IntegerField()
    genres = GenreSerializer(many=True, read_only=True)

    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True, source="genres", queryset=Genre.objects.all(), write_only=True
    )

    class Meta:
        model = Book
        fields = [
            "id",
            "name",
            "language",
            "publish_date",
            "page_number",
            "genre_ids",
            "genres",
        ]

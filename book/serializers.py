from rest_framework import serializers
from book.models import Book, Genre


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Genre
        fields = ["name"]


class BookSerializer(serializers.ModelSerializer):
    queryset = Book.objects.all()

    name = serializers.CharField()
    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    language = serializers.CharField()
    publish_date = serializers.DateField()
    page_number = serializers.IntegerField()
    book_type = serializers.CharField()

    class Meta:
        model = Book
        fields = [
            "name",
            "genres",
            "language",
            "publish_date",
            "page_number",
            "book_type",
        ]

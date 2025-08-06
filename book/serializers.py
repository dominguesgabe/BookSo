from rest_framework import serializers
from book.models import Genre


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = Genre
        fields = ["name"]

from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=150)
    genres = models.ManyToManyField(Genre, blank=True)
    language = models.CharField(max_length=50, blank=True, default="Português")
    publish_date = models.DateField()
    page_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

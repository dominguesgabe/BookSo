from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=150)
    genres = models.ManyToManyField(Genre)
    language = models.CharField(max_length=50, blank=True, default="Português")
    publish_date = models.DateField()
    page_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

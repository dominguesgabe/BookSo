from django.db import models


class Book(models.Model):
    GENRE_CHOICES = [
        ("romance", "Romance"),
        ("thriller", "Terror"),
        ("sci-fi", "Ficção Científica"),
        ("fantasy", "Fantasia"),
        ("adventure", "Aventura"),
        ("self-help", "Autoajuda"),
    ]

    title = models.CharField(max_length=150)
    genre = models.CharField(max_length=25, choices=GENRE_CHOICES)
    language = models.CharField(max_length=50, blank=True, default="Português")
    publish_date = models.DateField(blank=True)

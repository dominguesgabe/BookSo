from django.test import TestCase
from store.models import Product
from book.models import Book, Genre
from datetime import date


class ProductTestCase(TestCase):
    def setUp(self):
        book = Book.objects.create(
            name="A Fantástica Fábrica de Chocolate",
            publish_date=date.today(),
            page_number=100,
        )

        Genre.objects.create(name="Fantasy")
        genre_queryset = Genre.objects.all()
        book.genres.set(genre_queryset)

        Product.objects.create(
            book=book,
            available_quantity=1,
            price=10.5,
        )

    def test_check_if_book_exists(self):
        product = Product.objects.get(pk=1)

        self.assertIsInstance(product, Product)

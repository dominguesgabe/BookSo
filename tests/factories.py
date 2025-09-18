from datetime import date
from book.models import Genre, Book
from store.models import Product


def genre_factory():
    genre = Genre.objects.create(name="Fantasy")

    return genre


def book_factory():
    book = Book.objects.create(
        name="The amazing spider man - Chapter 1",
        publish_date=date.today(),
        page_number=100,
        language="English",
    )
    genre_factory()
    genre_queryset = Genre.objects.all()
    book.genres.set(genre_queryset)

    return book


def product_factory():
    book = book_factory()
    product = Product.objects.create(
        book=book,
        available_quantity=10,
        price=10.5,
    )

    return product


# book = Book.objects.create(
#             name="A Fantástica Fábrica de Chocolate",
#             publish_date=date.today(),
#             page_number=100,
#         )

#         Genre.objects.create(name="Juvenile")
#         genre_queryset = Genre.objects.all()
#         book.genres.set(genre_queryset)

#         Product.objects.create(
#             book=book,
#             available_quantity=1,
#             price=10.5,
#         )

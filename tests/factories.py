from datetime import date
from book.models import Genre, Book
from store.models import Product


def genre_factory():
    genre = Genre.objects.create(name="Fantasy")

    return genre


def book_factory(
    name="The amazing spider man - Chapter 1",
    publish_date=date.today(),
    page_number=125,
    language="English",
):
    book = Book.objects.create(
        name=name,
        publish_date=publish_date,
        page_number=page_number,
        language=language,
    )
    genre_factory()
    genre_queryset = Genre.objects.all()
    book.genres.set(genre_queryset)

    return book


def product_factory(
    book,
    available_quantity=10,
    price=10.5,
    product_type=Product.PHYSICAL,
):
    product = Product.objects.create(
        book=book,
        available_quantity=available_quantity,
        price=price,
        product_type=product_type,
    )

    return product

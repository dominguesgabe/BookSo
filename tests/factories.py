from datetime import date
from book.models import Genre, Book
from store.models import Product, Cart, CartItem, Customer
from django.contrib.auth.models import User


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
    *,
    book,
    available_quantity=10,
    price=10.5,
    product_type=Product.PHYSICAL,
    active=True,
):
    product = Product.objects.create(
        book=book,
        available_quantity=available_quantity,
        price=price,
        product_type=product_type,
        active=active,
    )

    return product


def customer_factory(user):
    customer = Customer.objects.create(user=user)

    return customer


def cart_factory(user):
    customer = customer_factory(user)
    cart = Cart.objects.get_or_create(customer=customer)

    return cart


def cart_item_factory(user):
    book = book_factory()
    product = product_factory(book)
    cart = cart_factory(user)

    cart_item = CartItem.objects.create(cart=cart, product=product)

    return cart_item

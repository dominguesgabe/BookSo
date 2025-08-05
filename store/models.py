from django.db import models
from django.contrib.auth.models import User
from book.models import Book
import uuid


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_out = models.BooleanField(default=False)


class Product(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    available_quantity = models.IntegerField()
    price = models.FloatField()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    ORDER_STATUS_CHOICES = {
        "pending": "Pendente",
        "processing": "Em processamento",
        "success": "Sucesso",
        "Error": "Erro",
    }

    code = models.UUIDField(default=uuid.uuid4, editable=False)
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

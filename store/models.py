from django.db import models
from django.contrib.auth.models import User
from book.models import Book
import uuid


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.id} - {self.customer.user.username}"


class Product(models.Model):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    PRODUCT_TYPE_CHOICES = [
        (PHYSICAL, "Físico"),
        (DIGITAL, "Digital"),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="product",
    )
    available_quantity = models.IntegerField()
    price = models.FloatField()
    product_type = models.CharField(
        max_length=10, choices=PRODUCT_TYPE_CHOICES, default=PHYSICAL
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.book.name


class CartItem(models.Model):
    # Nested relationship
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.price is None:
            # This thing is really cool
            self.price = self.product.price

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cart.__str__()} - {self.product.__str__()}"


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

    def __str__(self):
        return f"order {self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.product.__str__()

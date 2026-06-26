from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    checked_out_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"Cart {self.id} - {self.customer.user.username}"


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    def __str__(self):
        return self.name

    def full_path(self):
        path = [self.name]

        current = self.parent

        while current:
            path.insert(0, current.name)
            current = current.parent

        return " > ".join(path)

    class Meta:
        verbose_name_plural = "categories"


class Product(models.Model):
    name = models.CharField(max_length=350, blank=False)
    sku = models.CharField(max_length=20, unique=True, blank=False)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50, blank=True, default="Português")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_quantity = models.IntegerField()
    price = models.FloatField()
    active = models.BooleanField(default=True)
    external_price_id = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    url = models.CharField(blank=False)
    alt_text = models.CharField(max_length=250, blank=True)
    is_primary = models.BooleanField(default=False)


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

    total_price = models.FloatField()
    status = models.CharField(
        max_length=10, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    checked_out_at = models.DateTimeField(null=True)
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"Order #{self.id}"

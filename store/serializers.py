from rest_framework import serializers
from store.models import Cart, Customer, Product
from book.models import Book


class CartSerializer(serializers.ModelSerializer):
    queryset = Cart.objects.all()

    customer = serializers.PrimaryKeyRelatedField(
        many=False, source="id", queryset=Customer.objects.all()
    )

    class Meta:
        model = Cart
        fields = ["id", "customer"]


class CustomerSerializer(serializers.ModelSerializer):
    queryset = Customer.objects.all()

    class Meta:
        model = Customer
        fields = ["id"]


class ProductSerializer(serializers.ModelSerializer):
    queryset = Product.objects.all()

    book = serializers.PrimaryKeyRelatedField(
        many=False, source="id", queryset=Book.objects.all()
    )
    available_quantity = serializers.IntegerField()
    price = serializers.FloatField()

    class Meta:
        model = Product
        fields = ["id", "book", "available_quantity", "price"]

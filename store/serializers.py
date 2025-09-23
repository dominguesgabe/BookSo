from rest_framework import serializers
from store.models import Cart, CartItem, Customer, Product
from django.contrib.auth.models import User
from book.models import Book
from book.serializers import BookSerializer


class UserSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()

    username = serializers.CharField()
    full_name = serializers.SerializerMethodField()
    email = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email"]

    # Django have an intern method that do the same thing,
    # I just wanted to have an example saved on my codebase
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.first_name}".strip()


class CustomerSerializer(serializers.ModelSerializer):
    queryset = Customer.objects.all()

    user = serializers.SerializerMethodField()

    def get_user(self, obj: Customer):
        return UserSerializer(obj.user).data

    class Meta:
        model = Customer
        fields = ["user"]


class ProductSerializer(serializers.ModelSerializer):
    queryset = Product.objects.all()

    book_id = serializers.PrimaryKeyRelatedField(
        many=False, source="book", queryset=Book.objects.all(), write_only=True
    )
    book = BookSerializer(read_only=True)
    available_quantity = serializers.IntegerField()
    price = serializers.FloatField()
    product_type = serializers.ChoiceField(choices=Product.PRODUCT_TYPE_CHOICES)

    class Meta:
        model = Product
        fields = [
            "id",
            "available_quantity",
            "price",
            "product_type",
            "book",
            "book_id",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    queryset = CartItem.objects.all()

    # Nested relationship
    product_name = serializers.CharField(source="product.book.name", read_only=True)

    # improve product relation
    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "price"]


class CartSerializer(serializers.ModelSerializer):
    queryset = Cart.objects.all()

    # Nested relationship
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "created_at",
            "checked_out",
        ]


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

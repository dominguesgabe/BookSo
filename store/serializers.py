from rest_framework import serializers
from store.models import Cart, CartItem, Customer, Product
from django.contrib.auth.models import User


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

    available_quantity = serializers.IntegerField()
    price = serializers.FloatField()
    external_price_id = serializers.CharField(max_length=250, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "available_quantity",
            "price",
            "product_type",
            "external_price_id",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    queryset = CartItem.objects.all()

    product = ProductSerializer()

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
            "checked_out_at",
        ]


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class DefaultPriceSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=3, allow_null=True, default="brl")
    unit_amount_decimal = serializers.FloatField()


class ExternalProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    default_price_data = DefaultPriceSerializer(required=False)

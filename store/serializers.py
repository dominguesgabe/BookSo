from rest_framework import serializers
from store.models import Cart, Customer


class CartSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        many=False, source="genres", queryset=Customer.objects.all()
    )

    class Meta:
        model = Cart
        fields = ["id", "customer"]


class CustomerSerializer(serializers.ModelSerializer):
    queryset = Customer.objects.all()

    class Meta:
        model = Customer
        fields = ["id"]

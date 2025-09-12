from rest_framework import serializers
from store.models import Cart


class CartSerializer(serializers.ModelSerializer):
    # customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # created_at = models.DateTimeField(auto_now_add=True)
    # checked_out = models.BooleanField(default=False)
    class Meta:
        model = Cart
        fields = ["id"]

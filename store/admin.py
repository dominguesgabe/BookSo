from django.contrib import admin

from .models import Cart, CartItem, Customer, Product, Order


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)

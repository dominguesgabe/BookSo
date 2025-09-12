from django.contrib import admin

from .models import Cart, Customer


admin.site.register(Cart)
admin.site.register(Customer)
# admin.site.register(Order, OrderItem)

from django.contrib import admin
from bot.models import Product, Order, OrderItem

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)


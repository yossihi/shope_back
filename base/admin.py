from django.contrib import admin

from .models import Order, Order_Detail, Product


admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Order_Detail)

from django.contrib import admin
from .models import Product, Customer, Order , Category, Address, OrderItem, Cart, CartItem  # Import your models

# Register your models here.



admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(CartItem)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(OrderItem)
admin.site.register(Address)
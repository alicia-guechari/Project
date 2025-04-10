from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

# ************************************************Cart*******************************************************

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = CartItem
        fields = '__all__'

class CartItemInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity', 'cart']

# ************************************************Order*******************************************************

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')  # Show product name in response

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'subtotal']
 
class OrderSerializer(serializers.ModelSerializer): # this is a nested serialization
    items = OrderItemSerializer(many=True, read_only=True)  # Show order items
    user = serializers.ReadOnlyField(source='customer.email')  # Show customer email instead of its id

    class Meta:
        model = Order
        fields = ['user', 'total_price', 'status', 'created_at', 'items']


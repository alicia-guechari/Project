from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')  # Show product name in response

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'subtotal']
 
class OrderSerializer(serializers.ModelSerializer): # this is a nested serialization
    items = OrderItemSerializer(many=True, read_only=True)  # Show order items
    customer = serializers.ReadOnlyField(source='customer.email')  # Show customer email instead of its id

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_price', 'status', 'created_at', 'items']

from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True) #read-only means clients can see the product name but cannot modify it.
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "product_name", "product_price", "quantity", "subtotal"]
        read_only_fields = ["cart", "subtotal"]

from .models import Cart

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cartitem_set", many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price"]
        read_only_fields = ["user"] 

    def get_total_price(self, obj):
        return sum(item.subtotal for item in obj.cartitem_set.all())



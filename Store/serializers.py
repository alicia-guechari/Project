from rest_framework import serializers
from .models import *
from dj_rest_auth.serializers import UserDetailsSerializer

class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        model = Customer
        fields = UserDetailsSerializer.Meta.fields + ('phone',)

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
        read_only_fields = ['user']

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
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'subtotal']
 
class OrderSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            'username' : obj.user.username,
            'email' : obj.user.email,
            'phone' : obj.user.phone,
        }

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'total_price']

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'created_at', 'items']
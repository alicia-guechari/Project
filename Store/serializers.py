from rest_framework import serializers
from .models import *
from dj_rest_auth.serializers import UserDetailsSerializer, LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer


# from django.contrib.auth import authenticate
# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model

# class PhoneBackend(ModelBackend):
#     def authenticate(self, request, phone=None, password=None, **kwargs):
#         UserModel = get_user_model()
#         try:
#             user = UserModel.objects.get(phone=phone)
#             if user.check_password(password):
#                 return user
#         except UserModel.DoesNotExist:
#             return None

# class CustomLoginSerializer(LoginSerializer):
#     phone = serializers.CharField(required=True)
#     username = None

#     def validate(self, attrs):
#         phone = attrs.get('phone')
#         password = attrs.get('password')

#         if phone and password:
#             user = authenticate(request=self.context.get('request'), phone=phone, password=password)
#             if not user:
#                 raise serializers.ValidationError("Invalid phone or password.")
#         else:
#             raise serializers.ValidationError("Must include 'phone' and 'password'.")

#         attrs['user'] = user
#         return attrs
from chargily_pay.api import ChargilyClient
from chargily_pay.settings import CHARGILIY_URL
from chargily_pay.entity import Customer as Ch_Customer
from website import settings

class CustomRegisterSerializer(RegisterSerializer):
    phone = serializers.CharField(max_length=15)

    def custom_signup(self, request, user):
        user.phone = self.validated_data.get('phone', '')
        user.save()
    
    def save(self, request):
        user = super().save(request)
        try:
            chargily = ChargilyClient(settings.CHARGILI_PUBLIC_KEY, settings.CHARGILI_SECRET_KEY, CHARGILIY_URL)
            response = chargily.create_customer(Ch_Customer(name=user.username, email=user.email, phone=user.phone))
            user.chargily_id = response['id']
            user.save()
        except Exception as e:
            print(f'chargily error: {str(e)}')
        return user

class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        model = Customer
        fields = UserDetailsSerializer.Meta.fields + ('phone', 'is_staff',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

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
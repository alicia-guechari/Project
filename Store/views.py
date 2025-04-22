from rest_framework import status, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as django_filters
from .models import *
from .serializers import *


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        
        cart_item.save()
        return Response({"message": "item added to cart"}, status=status.HTTP_201_CREATED)

class ListCartItemsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer
    pagination_class = None

    def get_queryset(self):
        cart = Cart.objects.filter(user=self.request.user).first()
        return CartItem.objects.filter(cart=cart)

class CartItemManagerView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PUT', 'PATCH']:
            return CartItemInputSerializer
        return CartItemSerializer

class ClearCartView(APIView):
    parser_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart).delete()

        return Response({"message": "Cart cleared successfully"}, status=status.HTTP_204_NO_CONTENT)

# ---------------------------------------Product----------------------------------------------

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
    in_stock = django_filters.BooleanFilter(field_name="stock", lookup_expr='gt', exclude=True)

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'in_stock']

class ProductListCreateView(generics.ListCreateAPIView):  # for creation (only admin) and listing (all users)
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]  

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView): # update and delete (admin only) , get one prod (for public)
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]  

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer

class ProductSearchView(generics.ListAPIView): # for search and ordering and filtering 
    queryset = Product.objects.select_related('category').all() # is just a performance optimization
    serializer_class = ProductListSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'name']

# ---------------------------------------Category----------------------------------------------for admin

class CategoryView(generics.ListCreateAPIView):   #list and create (admin only)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]

class CategoryManagerView(generics.RetrieveUpdateDestroyAPIView): # retrieving, updating, and deleting a single category.
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

# ---------------------------------------Address----------------------------------------------

class AddressView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Address.objects.all()
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

# ---------------------------------------Order----------------------------------------------


from chargily_pay.api import ChargilyClient
from chargily_pay.settings import CHARGILIY_TEST_URL, CHARGILIY_URL
from chargily_pay.entity import Checkout
from website import settings

chargily = ChargilyClient(settings.CHARGILI_PUBLIC_KEY, settings.CHARGILI_SECRET_KEY, CHARGILIY_URL)

@api_view(['POST'])
def chargilyCheckout(request):
    response = chargily.create_checkout(
        Checkout(
            success_url='http://localhost:8000/store/order/' ,
            amount=540,
            currency='dzd',
            locale='en',
        ))
    return Response({'message':'checkouted', 'response':response})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    address = request.data.get('address')
    payement_method = request.data.get('payement_method')

    if not cart.items.exists():
        return Response({'error': 'cart is empty'}, status=400)
    total = cart.total_price()

    if payement_method != 'cash':
        # make e-payment
        pass    
    order = Order.objects.create(user=user, total_price=total, address=address, payement_method=payement_method)

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
        )
    cart.items.all().delete()
    return Response({'message': 'Order created successfully'})

class ListOrderView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

class OrderManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
        
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderDetailSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.request.method in ['DELETE', 'GET']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

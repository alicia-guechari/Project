
from rest_framework import status , viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import generics, mixins, permissions, filters
from django_filters import rest_framework as django_filters
from .models import *
from .serializers import *
from .permissions import IsOwnerOrAdmin
from django.shortcuts import get_object_or_404



# class OrderList(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """Retrieve all orders for an admin or only the user's orders."""
#         if request.user.is_staff:
#             orders = Order.objects.all()  # Admin sees all orders
#         else:
#             orders = Order.objects.filter(customer=request.user)  # Customers see only their orders
        
#         serializer = OrderSerializer(orders, many=True) # many cuz of many orders to serial
#         return Response(serializer.data)

# class OrderCreateView(APIView): #Inherits from APIView → This means it will handle HTTP requests (here it's post)
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic  # Ensures all DB operations are either completed or rolled back, if anything fails, all changes to the database are undone
#     def post(self, request):
#         """Create an order from the customer's cart."""
#         customer = request.user #Retrieves the authenticated user (who is placing the order).
#         cart = Cart.objects.filter(customer=customer).first() #first() ensures we get one cart (if it exists) else val=None

#         if not cart: #If the customer doesn't have a cart,
#             return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

#         cart_items = CartItem.objects.filter(cart=cart) #Fetches all items in the customer's cart.

#         if not cart_items.exists(): #If there are no items in the cart
#             return Response({'error': 'No items in the cart'}, status=status.HTTP_400_BAD_REQUEST)

#         total_price = sum(item.product.price * item.quantity for item in cart_items)
 
#         # Get address from request
#         address_id = request.data.get('address_id')  # Expecting address_id in request body
#         address = Address.objects.filter(id=address_id, customer=customer).first()

#         if not address:
#             return Response({'error': 'Invalid or missing address'}, status=status.HTTP_400_BAD_REQUEST)

#         # Create Order
#         order = Order.objects.create(customer=customer, total_price=total_price)

#         # Create OrderItems
#         for item in cart_items:
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 price=item.product.price  # Save price at the time of order
#             )
#             # Reduce stock (optional)
#             # item.product.stock -= item.quantity
#             # item.product.save()

#         # Clear cart after checkout
#         cart_items.delete()

#         serializer = OrderSerializer(order)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#                      ************************************
# the cart : 

# Retrieving the cart (GET)
# Adding an item to the cart (POST)
# Updating the quantity of an item (PATCH)
# Removing an item from the cart (DELETE)


# class CartView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """Retrieve the cart of the logged-in user."""
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         serializer = CartSerializer(cart)
#         return Response(serializer.data)

# class AddToCartView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """Add a product to the cart or update its quantity."""
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         product_id = request.data.get("product_id")
#         quantity = int(request.data.get("quantity", 1))

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
#         if not created:
#             cart_item.quantity += quantity  # Increase quantity if already exists
#         else:
#             cart_item.quantity = quantity  # Set quantity for new item
        
#         cart_item.save()
#         return Response({"message": "Item added to cart"}, status=status.HTTP_201_CREATED)

# class UpdateCartItemView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self, request, item_id):
#         """Update the quantity of an item in the cart."""
#         try:
#             cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
#         except CartItem.DoesNotExist:
#             return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

#         quantity = int(request.data.get("quantity", 1))
#         if quantity <= 0:
#             cart_item.delete()  # Remove item if quantity is 0
#             return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)

#         cart_item.quantity = quantity
#         cart_item.save()
#         return Response({"message": "Cart item updated"}, status=status.HTTP_200_OK)

# class RemoveCartItemView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, item_id):
#         """Remove an item from the cart."""
#         try:
#             cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
#             cart_item.delete()
#             return Response({"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)
#         except CartItem.DoesNotExist:
#             return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

# class ClearCartView(APIView):
#     permission_classes = [IsAuthenticated]

#     def deleteCart(self, request):
#         """Remove all items from the user's cart."""
#         cart = Cart.objects.filter(user=request.user).first()

#         if not cart:
#             return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Delete all cart items
#         CartItem.objects.filter(cart=cart).delete()

#         return Response({"message": "Cart cleared successfully"}, status=status.HTTP_204_NO_CONTENT)

# #                    ******************************************************************************

# class Cartt(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def list(self, request):
#         """Retrieve all cart items for the authenticated user."""
#         cart = Cart.objects.filter(user=request.user).first()
#         if not cart:
#             return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         cart_items = CartItem.objects.filter(cart=cart)
#         serializer = CartItemSerializer(cart_items, many=True)
#         return Response(serializer.data)

#     def create(self, request):
#         """Add an item to the cart."""
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         product_id = request.data.get("product_id")
#         quantity = int(request.data.get("quantity", 1))

#         if not product_id:
#             return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#         cart_item.quantity += quantity
#         cart_item.save()

#         return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

#     def delete(self, request, pk=None):
#         """Remove a specific item from the cart."""
#         try:
#             cart_item = CartItem.objects.get(id=pk, cart__user=request.user)
#             cart_item.delete()
#             return Response({"message": "Item removed"}, status=status.HTTP_204_NO_CONTENT)
#         except CartItem.DoesNotExist:
#             return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

#     @action(detail=False, methods=["delete"]) #This specifies that this action only accepts DELETE requests.
#     def clear(self, request):
#         """Custom action: Clear all cart items."""
#         cart = Cart.objects.filter(user=request.user).first()
#         if not cart:
#             return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

#         CartItem.objects.filter(cart=cart).delete()
#         return Response({"message": "Cart cleared successfully"}, status=status.HTTP_204_NO_CONTENT)



# ---------------------------------------Product----------------------------------------------

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(field_name="category__name", lookup_expr='iexact')
    in_stock = django_filters.BooleanFilter(field_name="stock", lookup_expr='gt', exclude=True)

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category', 'in_stock']

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]  

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductCreateSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]  

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductCreateSerializer

class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.select_related('category').all() # is just a performance optimization
    serializer_class = ProductListSerializer
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'name']

# ---------------------------------------Category----------------------------------------------for admin

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None
    permission_classes = [permissions.IsAdminUser]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
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

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

# ---------------------------------------Order----------------------------------------------


# from chargily_pay.api import ChargilyClient
# from chargily_pay.settings import CHARGILIY_TEST_URL

# key="chargilly-key"
# secret="chargily-secret"
# chargily = ChargilyClient(key, secret, CHARGILIY_TEST_URL)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    address = request.data.get('address')

    if not cart.items.exists():
        return Response({'error': 'cart is empty'}, status=400)

    total = cart.total_price()
    
    order = Order.objects.create(user=user, total_price=total, address=address)

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
        )

    cart.items.all().delete()

    return Response({'message': 'Order created successfully'})

from rest_framework import status, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as django_filters
from .models import *
from .serializers import *

import os
from django.db.models import Sum
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


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

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]  

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer

class ProductListCreateView(generics.ListCreateAPIView): 
    queryset = Product.objects.select_related('category').all()
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price']

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]  

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductListSerializer
        return ProductSerializer

# ---------------------------------------Category----------------------------------------------for admin

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]

class CategoryManagerView(generics.RetrieveUpdateDestroyAPIView):
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
from chargily_pay.entity import Checkout, Customer as Ch_Customer
from website import settings

chargily = ChargilyClient(settings.CHARGILI_PUBLIC_KEY, settings.CHARGILI_SECRET_KEY, CHARGILIY_URL)

def make_payment(amount, payment_method, id):
    user = Customer.objects.get(pk=id)
    chargily_id = user.chargily_id
    if not chargily_id:
        try:
            response = chargily.create_customer(Ch_Customer(name=user.username, email=user.email, phone=user.phone))
            user.chargily_id = response['id']
            chargily_id = response['id']
            user.save()
        except Exception as e:
            print(f'chargily error: {str(e)}')
        
    return chargily.create_checkout(
        Checkout(
            success_url='http://localhost:5173/orderconfirmation',
            failure_url='http://localhost:5173/cart',
            amount=amount,
            currency='dzd',
            locale='en',
            payment_method=payment_method,
            customer_id=chargily_id,
        ))

@api_view(['POST']) 
def chargilyCheckout(request):
    response = chargily.create_checkout(
        Checkout(
            success_url='http://localhost:5173/orderconfirmation',
            failure_url='http://localhost:5173/cart',
            amount=200.99,
            currency='dzd',
            locale='en',
            payment_method='edahabia',
            customer_id='01jtbkttpvs8p0yk90wwqxqt11',
        ))
    return Response({'response':response}) 

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    user = request.user
    address_id = request.data.get('address')
    payment_method = request.data.get('payment_method')

    address = get_object_or_404(Address, id=address_id) 
    cart = get_object_or_404(Cart, user=user)

    if not cart.items.exists():
        return Response({'error': 'cart is empty'}, status=400)
    
    total = cart.total_price()
    payment_response = None
    if payment_method != 'cash':
        try:
            payment_response = make_payment(float(total), payment_method, user.pk)
        except Exception as e:
            return Response({'error':str(e)})
    
    order = Order.objects.create(user=user, total_price=total, address=address, payment_method=payment_method)
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
        )
        
        product = item.product
        product.stock -= item.quantity
        product.save()
        
    cart.items.all().delete()
    return Response({'message': 'order created', 'payment_response': payment_response})

class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')

    class Meta:
        model = Order
        fields = ['status']

class ListOrderView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['created_at', 'total_price', 'status']
    ordering = ['-created_at']

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


# ---------------------------------------Total----------------------------------------------

class SiteStatisticsView(APIView):    
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):        
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_users = Customer.objects.count()        
        total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0        
        statistics = {            
            'total_products': total_products,
            'total_orders': total_orders,            
            'total_users': total_users,
            'total_revenue': total_revenue,            
        }
        return Response(statistics)

class BulkProductUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        if 'sheet' not in request.FILES:
            return Response({'error': 'No sheet file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        sheet_file = request.FILES['sheet']        
        if not sheet_file.name.endswith(('.xlsx', '.xls', '.csv')):
            return Response({'error': 'Unsupported sheet format. Please upload .xlsx, .xls, or .csv file'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        image_files = {}
        for key, file in request.FILES.items():
            if key != 'sheet' and file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                image_name = os.path.splitext(file.name)[0]
                image_files[image_name] = file
        
        try:
            if sheet_file.name.endswith('.csv'):
                df = pd.read_csv(sheet_file)
            else:
                df = pd.read_excel(sheet_file)
                
            required_columns = ['name', 'price', 'stock', 'category', 'image_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({'error': f'Missing required columns: {", ".join(missing_columns)}'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            products_created = 0
            products_updated = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    image_name = str(row['image_name']).strip()
                    image_file = image_files.get(image_name)
                    
                    if not image_file:
                        errors.append(f"Row {index+2}: Image '{image_name}' not found in uploaded files")
                        continue
                    

                    category_name = str(row['category'])
                    existing_category = Category.objects.filter(name__iexact=category_name).first()
                    if existing_category:
                        category = existing_category
                    else:
                        category = Category.objects.create(name=category_name)
                    
                    image_path = f'media/product/{image_file.name}'
                    saved_path = default_storage.save(image_path, ContentFile(image_file.read()))
                    
                    product_name = row['name']
                    existing_product = Product.objects.filter(name=product_name).first()
                    
                    if existing_product:
                        existing_product.price = float(row['price'])
                        existing_product.stock = int(row['stock'])
                        existing_product.category = category
                        existing_product.description = row.get('description', '')
                        existing_product.image = saved_path
                        existing_product.save()
                        products_updated += 1
                    else:
                        Product.objects.create(
                            name=product_name,
                            price=float(row['price']),
                            stock=int(row['stock']),
                            category=category,
                            description=row.get('description', ''),
                            image=saved_path
                        )
                        products_created += 1
                    
                except Exception as e:
                    from django.db import IntegrityError
                    if isinstance(e, IntegrityError) and "unique constraint" in str(e).lower():
                        errors.append(f"Row {index+2}: Product with name '{row['name']}' already exists")
                    else:
                        errors.append(f"Row {index+2}: {str(e)}")
            
            result_message = f'Created {products_created} products'
            if products_updated > 0:
                result_message += f', updated {products_updated} existing products'
            
            if errors:
                return Response({
                    'message': f'{result_message} with {len(errors)} errors',
                    'errors': errors
                }, status=status.HTTP_207_MULTI_STATUS)
                
            return Response({
                'message': result_message
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': f'Error processing file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

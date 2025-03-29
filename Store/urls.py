from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter # this if we use the cart viewset

router = DefaultRouter()
router.register(r'cart', Cart, basename='cart')

urlpatterns = [
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('products/search/', ProductSearchView.as_view()),

    path('categories/', CategoryView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),

    path('address/', AddressView.as_view()),
    path('address/<int:pk>/', AddressDetailView.as_view()),

    path("cart/", CartView.as_view(), name="cart"), 
    path("cart/add/", AddToCartView.as_view(), name="add_to_cart"),  
    path("cart/update/<int:item_id>/", UpdateCartItemView.as_view(), name="update_cart_item"), 
    path("cart/remove/<int:item_id>/", RemoveCartItemView.as_view(), name="remove_cart_item"),  
    path('cart/clear/', ClearCartView.as_view(), name='clear-cart'),
    path('', include(router.urls))
]


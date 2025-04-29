from django.urls import path, include
from .views import *

urlpatterns = [
    path('product/', ProductListCreateView.as_view()),
    path('product/<int:pk>/', ProductDetailView.as_view()),
    path('products/bulk-upload/', BulkProductUploadView.as_view()),

    path('category/', CategoryView.as_view()),
    path('category/<int:pk>/', CategoryManagerView.as_view()),

    path('address/', AddressView.as_view()),
    path('address/<int:pk>/', AddressDetailView.as_view()),

    path("cart/", ListCartItemsView.as_view()), 
    path("cart/add/", AddToCartView.as_view()),
    path("cart/<int:pk>/", CartItemManagerView.as_view()), 
    path('cart/clear/', ClearCartView.as_view()),

    path("order/", ListOrderView.as_view()),
    path("order/<int:pk>/", OrderManagerView.as_view()),
    path("order/checkout", checkout),

    path('statistics/', SiteStatisticsView.as_view()),
    path('chargily/', chargilyCheckout),
]


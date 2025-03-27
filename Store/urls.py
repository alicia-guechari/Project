from django.urls import path
from .views import *

urlpatterns = [
    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('products/search/', ProductSearchView.as_view()),

    path('categories/', CategoryView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),

    path('address/', AddressView.as_view()),
    path('address/<int:pk>/', AddressDetailView.as_view()),
]

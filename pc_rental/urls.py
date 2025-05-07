from django.urls import path
from .views import *

urlpatterns = [
    path('pcs/', PCListCreateView.as_view(), name='pc-list-create'),                   # GET, POST
    path('pcs/<int:pk>/', PCManagerView.as_view(), name='pc-detail'),                  # GET, PUT, PATCH, DELETE

    path('', ListRequestRent.as_view(), name='list-rentals'),                # GET, POST
    path('<int:pk>/', RentalManagerView.as_view(), name='rental-detail'),      # GET, PUT, PATCH, DELETE

    path('confirm-return/<int:rental_id>/', confirm_return, name='confirm-return'),  # POST
]

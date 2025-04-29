from django.urls import path
from .views import *

urlpatterns = [
    # PC management (admin only)
    path('pcs/', PCListCreateView.as_view(), name='pc-list-create'),                   # GET, POST
    path('pcs/<int:pk>/', PCManagerView.as_view(), name='pc-detail'),                  # GET, PUT, PATCH, DELETE

    # Rental
    path('', ListRequestPcRent.as_view(), name='list-rentals'),                # GET, POST
    path('<int:pk>/', RentalManagerView.as_view(), name='rental-detail'),      # GET, PUT, PATCH, DELETE

    # Confirm return (admin only)
    path('rentals/confirm-return/<int:rental_id>/', confirm_return, name='confirm-return'),  # POST
]

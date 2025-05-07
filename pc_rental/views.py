from rest_framework import generics, permissions, status
from .models import *
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import timedelta

from chargily_pay.api import ChargilyClient
from chargily_pay.settings import CHARGILIY_TEST_URL
from website import settings
from Store.views import make_payment
from django.utils.dateparse import parse_datetime


#   **********************************PCs*******************************

class PCListCreateView(generics.ListCreateAPIView):
    queryset = PC.objects.all() 
    serializer_class = PCSerializer 

    def get_permissions_class(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]

class PCManagerView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = PC.objects.all()
    serializer_class = PCSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [permissions.IsAdminUser()]

#   **********************************rental*******************************

chargily = ChargilyClient(settings.CHARGILI_PUBLIC_KEY, settings.CHARGILI_SECRET_KEY, CHARGILIY_TEST_URL)

class ListRequestRent(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Rental.objects.all().order_by('-is_active', '-rental_date')
        return Rental.objects.filter(user=self.request.user).order_by('-is_active', '-rental_date')
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ListingRentalSerializer
        return RentalSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return_date = request.data.get('return_date')
        return_datetime = parse_datetime(return_date)
        rental_date = request.data.get('rental_date')
        rental_datetime = parse_datetime(rental_date)        
        
        pc_id = request.data.get('pc')
        pc = get_object_or_404(PC, id=pc_id)
        pc.aviability_date = return_datetime + timedelta(days=2)
        pc.is_available = False
        pc.save()

        days = (return_datetime - rental_datetime).days
        total_price = days * pc.price_per_day
        serializer.save(user=self.request.user, total_price=total_price)
        headers = self.get_success_headers(serializer.data)
        
        payment_method = request.data.get('payment_method')
        payment_response = None
        if payment_method != 'cash':
            try:
                payment_response = make_payment(float(total_price), payment_method, self.request.user.pk)
            except Exception as e:
                return Response({'error':str(e)})

        return Response({'message':'','payment_response':payment_response}, status=status.HTTP_201_CREATED, headers=headers)

class RentalManagerView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RentalSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Rental.objects.all()
        return Rental.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def confirm_return(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)

    if not rental.is_active:
        return Response({'message': 'Rental already marked as returned'})

    rental.is_active = False
    rental.save()

    rental.pc.is_available = True
    rental.pc.save()
    return Response({'message': 'PC return confirmed successfully'})

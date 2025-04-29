from rest_framework import generics, permissions, status
from .models import *
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import timedelta

from chargily_pay.api import ChargilyClient
from chargily_pay.settings import CHARGILIY_TEST_URL
from chargily_pay.entity import Checkout
from website import settings

#   **********************************PCs*******************************

class PCListCreateView(generics.ListCreateAPIView):
    queryset = PC.objects.all() 
    serializer_class = PCSerializer 

    def get_permissions_class(self):
        if self.request.method == 'GET':
            print('==============================')
            return []
        return [permissions.IsAdminUser]

class PCManagerView(generics.RetrieveUpdateDestroyAPIView): #Retrieving, updating, and deleting a single PC instance.
    queryset = PC.objects.all()
    serializer_class = PCSerializer
    permission_classes = [permissions.IsAdminUser]

#   **********************************rental*******************************

chargily = ChargilyClient(settings.CHARGILI_PUBLIC_KEY, settings.CHARGILI_SECRET_KEY, CHARGILIY_TEST_URL)

@api_view(['POST'])
def chargilyCheckout(request):
    response = chargily.create_checkout(
        Checkout(
            success_url='http://google.com/',
            amount=540,
            currency='dzd',
            locale='en',
        ))
    return Response({'message':'checkouted', 'response':response})

class ListRequestPcRent(generics.ListCreateAPIView):
    serializer_class = RentalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Rental.objects.all()
        return Rental.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        from django.utils.dateparse import parse_datetime

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pc_id = request.data.get('pc')
        rental_date = request.data.get('rental_date')
        return_date = request.data.get('return_date')
        
        rental_datetime = parse_datetime(rental_date)
        return_datetime = parse_datetime(return_date)
        
        pc = get_object_or_404(PC, id=pc_id)        
        
        if pc.aviability_date and rental_datetime < pc.aviability_date:
            return Response({'error': 'PC is not available for the requested date'}, status=status.HTTP_400_BAD_REQUEST)
        
        pc.aviability_date = return_datetime + timedelta(days=2)
        pc.is_available = False
        pc.save()
        
        serializer.save(user=self.request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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

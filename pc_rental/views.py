from rest_framework import generics, permissions, status
from .models import *
from .serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import timedelta, datetime
from chargily_pay.api import ChargilyClient
from chargily_pay.settings import CHARGILIY_TEST_URL
from chargily_pay.entity import Checkout
from website import settings

class PCListCreateView(generics.ListCreateAPIView): #listing all pcs and creating a new one
    queryset = PC.objects.all()  # fetches all pcs from the DB
    serializer_class = PCSerializer 
    pagination_class = None
    permission_classes = [permissions.IsAdminUser] # only admins can acess this view

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

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rent_pc(request):
    user = request.user
    pc_id = request.data.get('pc_id')
    days = int(request.data.get('days', 1))

    pc = get_object_or_404(PC, id=pc_id)

    if not pc.is_available:
        return Response({'error': 'PC is not available'}, status=400)

    total_price = pc.price_per_day * Decimal(days)
    return_date = datetime.now() + timedelta(days=days)

    rental = Rental.objects.create(
        customer=user,
        pc=pc,
        return_date=return_date,
        total_price=total_price
    )
    
    pc.is_available = False
    pc.save()

    # # Create Chargily Checkout    # ***** chat suggested this , i don't know about is *****
    # response = chargily.create_checkout(
    #     Checkout(
    #         success_url='http://yourwebsite.com/rental-success/',
    #         amount=float(total_price),  # must be float
    #         currency='dzd',
    #         locale='en',
    #     ))

    # return Response({
    #     'message': 'Rental created successfully, proceed to payment',
    #     'rental_id': rental.id,
    #     'payment_link': response['checkout_url']
    # })

    
    return Response({'message': 'PC rented successfully'})


class ListRentalsView(generics.ListAPIView):
    serializer_class = RentalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Rental.objects.all()
        return Rental.objects.filter(customer=self.request.user)

class RentalManagerView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RentalSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Rental.objects.all()
        return Rental.objects.filter(customer=self.request.user)

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

from django.shortcuts import render
from rest_framework import generics
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

def health(request):
    return Response(status=status.HTTP_200_OK)

def register(request):
    data = request.data
    monthly_income = data.get('monthly_income')
    current_limit = round(36 * monthly_income, -5)
    customer_data = {
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'phone_number': data.get('phone_number'),
        'age': data.get('age'),
        'monthly_salary': monthly_income,
        'approved_limit': current_limit
    }
    if monthly_income < 0:
        return Response({'error': 'Monthly income should be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    elif customer_data['age'] < 0:
        return Response({'error': 'Age should be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        customer = Customer.objects.get(phone_number=customer_data['phone_number'])
        return Response({'error': 'Customer already exists'}, status=status.HTTP_400_BAD_REQUEST)
    except Customer.DoesNotExist:
        customer = Customer.objects.create(**customer_data)
        resp = {
            'customer_id': customer.customer_id,
            'name': customer.first_name + " " + customer.last_name,
            'age': customer.age,
            'phone_number': customer.phone_number,
            'approved_limit': customer.approved_limit
        }
        return Response(resp, status=status.HTTP_201_CREATED)

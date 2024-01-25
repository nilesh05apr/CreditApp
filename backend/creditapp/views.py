from django.shortcuts import render
from rest_framework import generics
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum
from rest_framework.decorators import api_view


# Create your views here.
def calculate_credit_score(customer):
    emis_paid_on_time = customer.loan_set.filter(emis_paid_on_time=True).count() or 0
    num_loans = customer.loan_set.count() or 0
    loan_activity_current_year = customer.loan_set.filter(start_date__year=timezone.now().year).count() or 0
    loan_approved_volume = customer.loan_set.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0

    credit_score = (emis_paid_on_time * 10) + (num_loans * 5) + (loan_activity_current_year * 15) + (loan_approved_volume // 10000)
    if credit_score > 100:
        credit_score = 100
    elif credit_score <= 0 or credit_score is None:
        credit_score = 10
    return credit_score

# def calculate_total_emi_percentage(customer):
#     total_emi_amount = customer.loan_set.aggregate(Sum('emi'))['emi__sum'] or 0
#     total_emi_percentage = (total_emi_amount / customer.monthly_income) * 100

#     return total_emi_percentage

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    monthly_interest_rate = (interest_rate / 100) / 12
    numerator = monthly_interest_rate * (1 + monthly_interest_rate) ** tenure
    denominator = (1 + monthly_interest_rate) ** tenure - 1

    monthly_installment = loan_amount * (numerator / denominator)

    return round(monthly_installment, 2)
@api_view(['GET'])
def health(request):
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def register(request):
    data = request.data
    print(data)
    monthly_income = data['monthly_income']
    current_limit = round(36 * monthly_income, -5)
    customer_data = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'phone_number': data['phone_number'],
        'age': data['age'],
        'monthly_salary': monthly_income,
        'approved_limit': current_limit
    }
    if 'approved_limit' in data.keys():
        customer_data['approved_limit'] = data['approved_limit']
    if 'customer_id' in data.keys():
        customer_data['customer_id'] = data['customer_id']
    else :
        customer_data['customer_id'] = Customer.objects.count() + 1
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

def validateInterestRate(interest_rate, credit_score):
    if (30 < credit_score <= 50) and interest_rate < 12:
        interest_rate = 12.0
    elif (10 < credit_score <= 30) and interest_rate < 16:
        interest_rate = 16.0 
    elif credit_score <= 10 and interest_rate < 16:
        interest_rate = 16.0
    else:
        return interest_rate
    return interest_rate

def CheckApproval(data):
    credit_score  = 0
    customer_id = data['customer_id']
    interest_rate = data['interest_rate']

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        total_emi = customer.loan_set.aggregate(Sum('emi'))['emi__sum'] or 0
        if total_emi > customer.monthly_salary * 0.5:
            approval = {'message': 'Customer has reached maximum EMI limit', 'approval': False}
        credit_score = calculate_credit_score(customer)
        interest_rate = validateInterestRate(interest_rate, credit_score)
        if credit_score > 50:
            approval = {'message': 'Loan approved with interest_rate:{interest_rate}', 'approval': True}
        elif 30 < credit_score <= 50:
            approval = {'message': 'Loan approved with interest_rate:{interest_rate}', 'approval': True}
        elif 10 < credit_score <= 30:
            approval = {'message': 'Loan approved with interest_rate:{interest_rate}', 'approval': True}
        else:
            approval = {'message': 'Loan rejected', 'approval': False}
        return approval    
    except Customer.DoesNotExist:
        return Response({'error': 'Customer does not exist'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def checkEligibility(request):
    credit_score  = 0
    data = request.data
    print(data)
    customer_id = data['customer_id']
    interest_rate = data['interest_rate']
    loan_amount = data['loan_amount']
    tenure = data['tenure']

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        credit_score = calculate_credit_score(customer)
        print(f"credit score of the customer: ",credit_score)
        corrected_interest_rate = validateInterestRate(interest_rate, credit_score)
        print("corrected interest rate for customer: ",corrected_interest_rate)
        response_data = {
            'customer_id': customer_id,
            'approval': CheckApproval(data)['approval'],
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'loan_amount': loan_amount,
            'tenure': tenure,
            'monthly_installment': calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure),
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer does not exist'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def createLoan(request):
    print(request.data)
    customer_id = request.data['customer_id']
    loan_amount = request.data['loan_amount']
    tenure = request.data['tenure']
    interest_rate = request.data['interest_rate']

    try:
        customer = Customer.objects.get(customer_id=customer_id)
        credit_score = calculate_credit_score(customer)
        corrected_interest_rate = validateInterestRate(interest_rate, credit_score)
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
        approval = CheckApproval(request.data)['approval']
        if approval:
            loan_data = {
                'customer_id': customer_id,
                'loan_amount': loan_amount,
                'tenure': tenure,
                'interest_rate': corrected_interest_rate,
                'emi': monthly_installment,
                'emis_paid_on_time': 0,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timezone.timedelta(days=tenure * 30)
            }
            try:
                loan = Loan.objects.create(**loan_data)
                response_data = {
                    'loan_id': loan.loan_id,
                    'customer_id': loan.customer_id,
                    'loan_approved': True,
                    'message': approval['message'].format(interest_rate=corrected_interest_rate),
                    'loan_amount': loan.loan_amount,
                    'monthly_installment': loan.emi,
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            except:
                return Response({'error': 'Loan creation failed'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Loan rejected'}, status=status.HTTP_200_OK)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer does not exist'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def viewLoanById(request):
    data = request.data
    loan_id = data['loan_id']
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        customer = Customer.objects.get(customer_id=loan.customer_id)
        response_data = {
            'loan_id': loan.loan_id,
            'customer': {
            'customer_id': loan.customer_id,
            'customer_name': customer.first_name + " " + customer.last_name,
            'customer_age': customer.age,
            'customer_phone_number': customer.phone_number,
            'customer_approved_limit': customer.approved_limit
            },
            'loan_amount': loan.loan_amount,
            'tenure': loan.tenure,
            'interest_rate': loan.interest_rate,
            'emi': loan.emi,
        }
    except Loan.DoesNotExist:
        return Response({'error': 'Loan does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def viewLoanByCustomerId(request):
    customer_id = request.data['customer_id']
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer_id=customer_id)
        response_data ={}
        for loan in loans:
            response_data[loan.loan_id] = {
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'emi': loan.emi,
                'repayments_left': loan.tenure - loan.emis_paid_on_time
            }
    except Customer.DoesNotExist:
        return Response({'error': 'Customer does not exist'}, status=status.HTTP_400_BAD_REQUEST)
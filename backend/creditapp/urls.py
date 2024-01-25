from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health, name='health'),
    path('register/', views.register, name='register'),
    path('check-eligibility/', views.checkEligibility, name='check-eligibility'),
    path('create-loan/', views.createLoan, name='create-loan'),
    path('view-loans/<int:customer_id>', views.viewLoanByCustomerId, name='view-loans'),
    path('view-loan/<int:loan_id>', views.viewLoanById, name='view-loan'),

]
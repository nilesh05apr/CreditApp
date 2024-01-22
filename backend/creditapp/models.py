from django.db import models

# Create your models here.
class Customer(models.Model):
    customer_id = models.IntegerField(auto_created=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.IntegerField(primary_key=True, unique=True)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Loan(models.Model):
    loan_id = models.IntegerField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    emi = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.loan_id
    
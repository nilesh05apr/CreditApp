# Generated by Django 5.0.1 on 2024-01-25 16:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("customer_id", models.IntegerField(auto_created=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("age", models.IntegerField()),
                (
                    "phone_number",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("monthly_salary", models.IntegerField()),
                ("approved_limit", models.IntegerField()),
                ("current_debt", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Loan",
            fields=[
                ("loan_id", models.IntegerField(primary_key=True, serialize=False)),
                ("loan_amount", models.FloatField()),
                ("tenure", models.IntegerField()),
                ("interest_rate", models.FloatField()),
                ("emi", models.FloatField()),
                ("emis_paid_on_time", models.IntegerField()),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "customer_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="creditapp.customer",
                    ),
                ),
            ],
        ),
    ]

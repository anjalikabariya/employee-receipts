from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=250, unique=True)
    password = models.CharField(max_length=250)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    age = models.PositiveSmallIntegerField(default=18)
    gender = models.CharField(null=True, max_length=30)

class Expense(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    expense_id=models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at =  models.DateTimeField()

    indexes = [
        models.Index(fields=['created_at', 'customer',]),
    ]
    
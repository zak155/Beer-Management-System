# Customer/models.py
from django.db import models
from Agent.models import Customer, Product_in_Agent_Stor, Driver
from Company.models import Product

class Customer_order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Not Recived', 'Not Recived'),
        ('Delivered', 'Delivered'),
    ) 
    Driver_choice = (
        ('Assigned', 'Assigned'),
        ('Not Assigned', 'Not Assigned'),
    ) 
    Customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    driver_status = models.CharField(max_length=200, null=True, choices=Driver_choice)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS, default='Not Assigned')

    def __str__(self) -> str:
        return str(self.Customer) + " | Order " + str(self.id)


class Customer_Transaction(models.Model):
    Paid_status_choices = (
        ('Paid', 'Paid'),
        ('Not Paid', 'Not Paid'),
    ) 
    Customer_order_id = models.OneToOneField(Customer_order, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    Total_Amount = models.FloatField(default=0.0, null=True, blank=True) 
    Paid_status = models.CharField(max_length=200, null=True, choices=Paid_status_choices)
  
    # Legacy fields (kept for safety & existing records)
    TransactionCode = models.CharField(max_length=200, null=True, blank=True)
    MarchentId = models.CharField(max_length=200, null=True, blank=True)
  
    # New Chapa tracking fields
    tx_ref = models.CharField(max_length=255, unique=True, null=True, blank=True)
    currency = models.CharField(max_length=10, default='ETB', null=True, blank=True)
    provider_status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.tx_ref or self.TransactionCode or self.id)
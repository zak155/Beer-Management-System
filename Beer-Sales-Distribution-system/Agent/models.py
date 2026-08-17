from django.db import models
from django.contrib.auth.models import User
from Company.models import Agent, Product, Company_Store

# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    Agent = models.ForeignKey(Agent, null=True, on_delete=models.CASCADE)
    #driver=models.ManyToManyField(Driver, null=True,on_delete=models.CASCADE)
    Compan_name = models.CharField(max_length=200, null=True)
    phone1 = models.CharField(max_length=200, null=True)
    phone2 = models.CharField(max_length=200, null=True)
    Address = models.CharField(max_length=200, null=True)
    House_No = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(
        null=True, blank=True, upload_to='Profile/')
    TIN_NO = models.CharField(max_length=500, null=True)
    License = models.FileField(null=True, blank=True, upload_to='License')
    Marchent_id = models.CharField(max_length=200, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.user)


class Agent_Store(models.Model):
    Store_Name = models.CharField(max_length=200, null=True)
    Location = models.CharField(max_length=200, null=True)


class Vehicle(models.Model):
    Product_Type = (
        ('Fetch track:', 'Fetch track'),
        ('Distribution track', 'Distribution track'),)
    vichel_name = models.CharField(max_length=100, null=True)
    vichel_type = models.CharField(
        max_length=200, null=True, choices=Product_Type)
    vichel_No = models.CharField(max_length=200, null=True,)
    vichel_pic = models.ImageField(
        null=True, blank=True, upload_to='vichel_pic/')

    Agent = models.ForeignKey(
        Agent, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.vichel_name


class Driver(models.Model):
    status_Type = (
        ('on_duty', 'on_duty'),
        ('on_garage', 'on_garage'),
        ('on_wating', 'on_wating'),
    )
    Status = models.CharField(
        max_length=200, null=True, choices=status_Type, default='on_wating')
    Full_name = models.CharField(max_length=200, null=True)
    Agent = models.ForeignKey(Agent, null=True, on_delete=models.CASCADE)
    vehicle = models.OneToOneField(
        Vehicle, null=True, blank=True, on_delete=models.CASCADE)
    phone1 = models.CharField(max_length=200, null=True)
    salary = models.CharField(max_length=500, null=True)
    profile_pic = models.ImageField(
        null=True, blank=True, upload_to='Profile/')
    Drive_license = models.FileField(
        null=True, blank=True, upload_to='License')
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.Full_name


class Agent_finance(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    Agent = models.OneToOneField(Agent, null=True, on_delete=models.CASCADE)
    phone1 = models.CharField(max_length=200, null=True)
    Adderes = models.CharField(max_length=200, null=True)
    about = models.TextField(null=True, blank=True, max_length=500)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    Telegram = models.CharField(max_length=200, null=True)
    facebook = models.CharField(max_length=200, null=True)
    instagrm = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.user.first_name


class Product_in_Agent_Stor(models.Model):
    Product_Type = (
        ('castel', 'castel'),
        ('senq', 'senq'),
        ('doppel', 'doppel'),
        ('george', 'george'),
    )

    Type = models.CharField(max_length=200, null=True, choices=Product_Type)
    Store = models.OneToOneField(
        Agent_Store, null=True, on_delete=models.CASCADE)
    price = models.FloatField(null=True)
    Agent = models.OneToOneField(Agent, null=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True)
    date_created = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.Type


class Agent_order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Recived', 'Recived'),
        ('Reject', 'Reject'),

    )

    Agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True)
    Store = models.ForeignKey(
        Company_Store, on_delete=models.CASCADE, null=True)
    date_created = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)

    def __str__(self) -> str:
        return str(self.id)


#products = Product.objects.all()
#for product in products:
    #Agent_order.add_to_class(product.Product_Name,
                             #models.IntegerField(default=0))


class Agent_Transaction(models.Model):
    Paid_status = (
        ('Paid', 'Paid'),
        ('Not Paid', 'Not Paid'),
    )
    Agent_order_id = models.OneToOneField(
        Agent_order, on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    Total_Amount = models.FloatField(null=True)
    Paid_status = models.CharField(
        max_length=200, null=True, choices=Paid_status)
    TransactionCode = models.CharField(max_length=200, null=True)
    MarchentId = models.CharField(max_length=200, null=True, )
    scheduled_for = models.DateField(auto_now_add=False, null=True, blank=True)
    scheduled_to = models.DateField(auto_now_add=False, null=True, blank=True)


class Customers_message(models.Model):
    agent = models.ForeignKey('Company.Agent', on_delete=models.CASCADE)
    email = models.TextField(max_length=200, blank=True, null=True)
    mssg = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=False)

#from distutils.command.upload import upload
#import imp
#from pyexpat import model
#from sre_constants import CATEGORY
#from statistics import mode
#from telnetlib import STATUS
#from tkinter import ON
#from turtle import title
#from unicodedata import category, name
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinLengthValidator

class Customer(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    locality=models.CharField(max_length=200)
    city=models.CharField(max_length=200)
    pincode=models.IntegerField()
    landmark=models.CharField(max_length=200)

    def __str__(self): 
        return str(self.id)

CATEGORY_CHOICES=(
    ('Men','Men'),
    ('Women','Women'),
    ('Child','Child'),
)

class Product(models.Model):
    title=models.CharField(max_length=100)
    selling_price=models.FloatField()
    discounted_price=models.FloatField()
    description=models.TextField()
    brand=models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES,max_length=5)
    product_image=models.ImageField(upload_to='productimg')

    def __str__(self):
        return str(self.id)
    
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return str(self.id)
    
    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

STATUS_CHOICES ={
('Accepted','Accepted'),
('Packed','Packed'),
('On the way','On the way'),
('Delivered','Delivered'),
('Cancel','Cancel'),
}
class OrderPlaced(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    Customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveBigIntegerField(default=1)
    ordered_date=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price

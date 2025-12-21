from django.db import models
from userapp.models import Customer
from productsapp.models import Products

# Create your models here.

class Cart(models.Model):
    user=models.ForeignKey(Customer,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    cartQty = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('user','product')
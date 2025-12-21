from rest_framework.serializers import ModelSerializer
from .models import Cart
from productsapp.serializers import ProductSerializer
from rest_framework import serializers

class CartSeriallizer(ModelSerializer):
    product = ProductSerializer(read_only = True)

    class Meta:
        model = Cart
        fields = ['id','product','cartQty']
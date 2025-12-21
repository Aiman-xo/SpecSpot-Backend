from rest_framework.serializers import ModelSerializer
from .models import Order,OrderItem,ShippingAddress
from productsapp.models import Products
from rest_framework import serializers
from productsapp.serializers import ProductSerializer
from userapp.models import Customer

class OrderItemSerializer(ModelSerializer):
    product= ProductSerializer(read_only=True)
    class Meta:
        model=OrderItem
        fields=['product','qty','price']

class ShippingAdressSerializer(ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields=[
            "fullname",
            "mainAddress",
            "phone",
            "city",
            "region",
            "pin",
            "country",
            ]

class OrderSerializer(ModelSerializer):
    username = serializers.CharField(source='user.name', read_only=True)
    items = OrderItemSerializer(many=True,read_only=True)
    shipping=ShippingAdressSerializer(read_only=True)
    total_amount = serializers.SerializerMethodField()
    class Meta:
        model=Order
        fields=['id','order_status','created_at','total_amount','items','shipping','username']
    
    def get_total_amount(self,obj):
        return sum( item.price * item.qty for item in obj.items.all())
    
class OrderStatusSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields=['order_status']

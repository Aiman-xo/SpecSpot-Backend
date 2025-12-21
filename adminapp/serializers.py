from rest_framework import serializers
from userapp.models import Customer
from ordersapp.models import Order,OrderItem
from django.db.models import Sum

class AdminUserSerializer(serializers.ModelSerializer):
    total_orders = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()
    class Meta:
        model =Customer
        fields=[
            'id',
            'name',
            'email',
            'is_active',
            'total_orders',
            'total_products'
        ] 
        read_only_fields=['is_active']

    def get_total_orders(self,obj):
        return Order.objects.filter(user=obj).count()
        
    def get_total_products(self,obj):
        total = OrderItem.objects.filter(order__user = obj).aggregate(total=Sum("qty"))['total']
        return total or 0

class RecentOrdersSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.name')
    class Meta:
        model = Order
        fields=['id','username','order_status']

class SalesTrendSerializer(serializers.Serializer):
    date = serializers.SerializerMethodField()
    count = serializers.IntegerField()

    def get_date(self, obj):
        return obj['date'].strftime("%b %d")
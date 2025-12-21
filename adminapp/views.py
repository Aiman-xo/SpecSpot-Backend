from django.shortcuts import render
from django.db.models import Sum,F,Count
from django.db.models.functions import TruncDay
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from userapp.models import Customer
from productsapp.models import Products
from ordersapp.models import Order,OrderItem
from .serializers import AdminUserSerializer,RecentOrdersSerializer,SalesTrendSerializer
from django.db.models import Q

# Create your views here.

class AdminUserView(APIView):
    permission_classes = [IsAdminUser]
    def get(self,request):
        search = request.GET.get("search", "").strip()
        status_filter = request.GET.get('status','').strip()
        users = Customer.objects.filter(is_staff=False)
        if search:
            users = users.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search)
            )
        
        total_users = users.count()

        if status_filter =='Active':
            users = users.filter(is_active=True)
        elif status_filter=='Inactive':
            users = users.filter(is_active=False)
            
        users = users.order_by("-id")

        serializer = AdminUserSerializer(users,many=True)
        return Response({'result':serializer.data,'total_users':total_users},status=status.HTTP_200_OK)

class AdminBlockUser(APIView):
    permission_classes=[IsAdminUser]
    def post(self,request,pk):
        try:
            user = Customer.objects.get(pk=pk,is_staff=False)
            user.is_active = not user.is_active
            user.save()
            status_msg = "unblocked" if user.is_active else "blocked"
            return Response({"message": f"{status_msg} successfully"})
        except Customer.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
class AdminDashboardView(APIView):
    permission_classes=[IsAdminUser]
    def get(self,request):
        total_users = Customer.objects.count()
        total_orders = Order.objects.count()
        total_products = Products.objects.filter(is_deleted = False).count()

        total_revenue = (
            OrderItem.objects.aggregate(revenue =Sum(F('price') * F('qty')) )['revenue'] or 0
        )

        recent_orders = (
            Order.objects.select_related('user').order_by('-created_at')[:6]
        )
        recent_order_datas = RecentOrdersSerializer(recent_orders,many=True).data

        order_status_pie=dict(
            Order.objects.values('order_status').annotate(count = Count('id')).values_list('order_status','count')
        )

        sales_trend_query =( 
            Order.objects.annotate(date=TruncDay('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        sales_trends = SalesTrendSerializer(sales_trend_query,many=True).data

        recent_users = (
            Customer.objects
            .order_by("-last_login")[:6]
        )

        recent_users_data = [
            {
                "name": user.name,
                "is_staff": user.is_staff
            }
            for user in recent_users
        ]

        return Response({
            "stats": {
                "total_users": total_users,
                "total_orders": total_orders,
                "total_products": total_products,
                "total_revenue": float(total_revenue),
            },
            "recent_orders": recent_order_datas,
            "order_status_distribution": order_status_pie,
            "sales_trends": sales_trends,
            "recent_users": recent_users_data,
        })
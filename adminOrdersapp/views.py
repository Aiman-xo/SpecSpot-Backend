from django.shortcuts import render
from django.db.models import Count
from math import ceil
from rest_framework.views import APIView
from ordersapp.models import Order,OrderItem,ShippingAddress
from ordersapp.serializers import OrderStatusSerializer
from ordersapp.serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
# Create your views here.

class AdminOrderView(APIView):
    permission_classes=[IsAdminUser]
    def get(self, request):
        page = int(request.GET.get("page", 1))
        limit = 5
        offset = (page - 1) * limit

        orders = (
            Order.objects
            .select_related("user")
            .prefetch_related("items", "shipping")
            .order_by("-created_at")
        )

        order_status = request.query_params.get("order_status")
        if order_status:
            orders = orders.filter(order_status=order_status)

        #  TOTAL AFTER FILTER (for has_next)
        total_count = orders.count()
        has_next = offset + limit < total_count
        total_pages = ceil(total_count/limit)

        #  PAGINATION
        orders = orders[offset:offset + limit]

        serializer = OrderSerializer(orders, many=True,context={"request": request})

        count = (
            Order.objects
            .values("order_status")
            .annotate(count=Count("id"))
        )

        total_orders = Order.objects.count()

        return Response({
            "result": serializer.data,
            "count": count,
            "total_orders": total_orders,
            "has_next": has_next,
            "page": page,
            "total_pages":total_pages
        }, status=status.HTTP_200_OK)

class AdminOrderStausView(APIView):
    permission_classes = [IsAdminUser] 
    def patch(self,request,pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error':'couldnt find that order!'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderStatusSerializer(order,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'orders status updated','data':serializer.data},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order,OrderItem,ShippingAddress
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework import status
from .serializers import OrderItemSerializer,OrderSerializer
import razorpay
import hmac
import hashlib
from django.conf import settings
# Create your views here.


razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)
class CreateOrderView(APIView):
    permission_classes =[IsAuthenticated]
    
    @transaction.atomic
    def post(self,request):
        user = request.user

        products = request.data.get('products')
        shipping_details = request.data.get('shipping')

        if not products or not shipping_details:
            return Response({'error':'products and shipping details must include'})
        
        order = Order.objects.create(user=user)
        items=[
            OrderItem(
                order=order,
                product_id = item['id'],
                qty=item['cartQty'],
                price = item['price']

            )

            for item in products
        ]
        OrderItem.objects.bulk_create(items)
        
            
        ShippingAddress.objects.create(order=order,**shipping_details)
        return Response({
            "message": "Order placed successfully",
            "order_id": order.id
        }, status=201)
    
    def get(self,request):
        orders=(
            Order.objects.filter(user=request.user)
            .select_related("shipping")
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
        serializer = OrderSerializer(orders,many=True,context={"request": request})
        return Response(serializer.data, status=200)

class DeleteOrderView(APIView):
    def delete(self,request,delete_id):
        try:
            order = Order.objects.get(id = delete_id,user=request.user)
        except Order.DoesNotExist:
            return Response({'error':'could not get that product'},status=404)
        
        if order.order_status in ["delivered", "shipped"]:
            return Response(
                {"error": "This order cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.order_status = "cancelled"
        order.save()

        return Response({"message": "Order cancelled successfully"}, status=200)


class RazorpayCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user

        products = request.data.get("products")
        shipping_details = request.data.get("shipping")

        if not products or not shipping_details:
            return Response({"error": "Products and shipping details are required"}, status=400)

        #  Create order in DB (but payment not done yet)
        order = Order.objects.create(user=user)

        #  Create all order items
        items = [
            OrderItem(
                order=order,
                product_id=item["id"],
                qty=item["cartQty"],
                price=item["price"]
            )
            for item in products
        ]
        OrderItem.objects.bulk_create(items)

        #  Create shipping details
        ShippingAddress.objects.create(order=order, **shipping_details)

        #  Calculate total amount
        total_amount = sum(float(item["price"]) * int(item["cartQty"] ) for item in products)
        total_amount+=total_amount*0.1 + 10
        amount_in_paise = int(total_amount * 100)


        #  Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": 1
        })

        # Save Razorpay order ID
        order.razorpay_order_id = razorpay_order["id"]
        # order.payment_status = "pending"
        order.save()

        # Send details to frontend
        return Response({
            "order_id": order.id,
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": amount_in_paise,
            "currency": "INR"
        }, status=201)

class RazorpayVerifyPaymentView(APIView):
    """
    Verify payment signature AND confirm actual payment.status via Razorpay API.
    If payment.status == "captured" -> mark paid.
    Otherwise -> mark failed + cancelled.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")

        if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
            return Response(
                {"status": "failed", "message": "Missing parameters"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1) verify signature
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()

        if expected_signature != razorpay_signature:
            # Signature mismatch -> treat as failed
            order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if order:
                order.payment_status = "failed"
                order.order_status = "cancelled"
                order.save()
            return Response({"status": "failed", "message": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # 2) Signature OK -> fetch payment details from Razorpay to confirm status
        try:
            payment_obj = razorpay_client.payment.fetch(razorpay_payment_id)
        except Exception as e:
            # If we cannot fetch payment details, mark failed (safer) and return error
            order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if order:
                order.payment_status = "failed"
                order.order_status = "cancelled"
                order.save()
            return Response({"status": "failed", "message": "Could not fetch payment details"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Razorpay payment_obj has a "status" field: "created", "authorized", "captured", "failed", etc.
        payment_status = payment_obj.get("status", "").lower()

        order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if not order:
            return Response({"status": "failed", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if payment_status == "captured":
            # Real success
            order.payment_status = "paid"
            order.order_status = "processing"
            order.save()
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        else:
            # Any other status -> treat as failed (including "failed")
            order.payment_status = "failed"
            order.order_status = "cancelled"
            order.save()
            return Response({"status": "failed", "message": f"Payment not captured (status={payment_status})"}, status=status.HTTP_400_BAD_REQUEST)
        
class RazorpayCancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")

        order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if not order:
            return Response({"message": "Order not found"}, status=404)

        # Mark as failed/cancelled
        order.payment_status = "failed"
        order.order_status = "cancelled"
        order.save()

        return Response({"status": "cancelled"}, status=200)

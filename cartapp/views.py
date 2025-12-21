from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CartSeriallizer
from rest_framework.permissions import IsAuthenticated
from productsapp.models import Products
from .models import Cart

# Create your views here.
class CartView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        
        item = (
            Cart.objects.filter(user = request.user)
            .select_related('product')
        )

        serializer = CartSeriallizer(item,many=True,context={"request": request})
        return Response(serializer.data)
    
    def post(self,request):
        product_id = request.data.get('product_id')
        qty = int(request.data.get('cartQty'))

        if not product_id:
            return Response({"error": "product_id is required"}, status=400)
        
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({'error':'product id didnt found'})
        
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )
        if  created:
            cart_item.cartQty = qty
            cart_item.save()
        else:
            return Response(
            {"message": "exists", "item": cart_item.id},
            status=200
        )

        serializer = CartSeriallizer(cart_item)
        return Response(serializer.data, status=200)

    def delete(self, request, product_id=None):
    # Case 1: DELETE specific product
        if product_id is not None:
            deleted, _ = Cart.objects.filter(
                user=request.user,
                product_id=product_id
            ).delete()

            if deleted:
                return Response({"message": "Product removed from cart"}, status=200)
            return Response({"error": "Product not found in cart"}, status=404)

        # Case 2: DELETE ALL cart items
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared"}, status=200)

    
    def patch(self,request,product_id):
        action = request.data.get('action')

        try:
            product = Cart.objects.get(user=request.user,product_id=product_id)
        except Cart.DoesNotExist:
            return Response({'error':'could not get that product'},status=404)
        
        if action == "increase":
            product.cartQty += 1
            product.save()
            return Response({"message": "increased", "qty": product.cartQty})
        elif action=='decrease':
            if product.cartQty > 1:
                product.cartQty -= 1
                product.save()
                return Response({"message": "decreased", "qty": product.cartQty})
        else:
            return Response({"message": "min_reached", "qty": product.cartQty})
        
        return Response({"error": "Invalid action"}, status=400)

from django.shortcuts import render
from .models import Wishlist
from productsapp.models import Products
from .serializers import WishlistSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
class WishlistView(APIView):
    def get(self,request):
        item = (
            Wishlist.objects.filter(user = request.user)
            .select_related('product')
        )

        serializer = WishlistSerializer(item,many=True,context={"request": request})  
        return Response(serializer.data)
    
    def post(self,request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "product_id is required"}, status=400)
        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({'error':'product id didnt found'})
        wishlist_item, created =Wishlist.objects.get_or_create(user=request.user, product=product)
        if not created:
            return Response({"message": "already_exists"}, status=200)
        return Response({"message": "Product added to wishlist"}, status=200)
    
    def delete(self,request,product_id):
        deleted, _ = Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
        ).delete()

        if deleted:
            return Response({"message": "Product removed from wishlist"}, status=200)

        return Response({"error": "Product not found in wishlist"}, status=404)
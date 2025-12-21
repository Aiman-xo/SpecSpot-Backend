from django.shortcuts import render
from .serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Products

# Create your views here.
class ProductView(ReadOnlyModelViewSet):
    queryset = Products.objects.filter(is_deleted=False).order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProductInduvidualView(APIView):
    def get(self,request,id):
        try:
            product = Products.objects.get(id=id)
        except Products.DoesNotExist:
            return Response({'error':'invalid product'},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductSerializer(product,context={"request": request})
        return Response(serializer.data,status=status.HTTP_200_OK)
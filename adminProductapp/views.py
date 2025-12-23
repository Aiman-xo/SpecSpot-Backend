from django.shortcuts import render
from productsapp.models import Products
from rest_framework.permissions import IsAdminUser
from productsapp.models import ProductCategory
from productsapp.serializers import ProductSerializer,ProductCategorySerializer
from rest_framework import viewsets,status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

# Create your views here.

class AdminProductsPagination(PageNumberPagination):
    page_size = 5
    page_query_param='page'
class AdminProductView(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes=[IsAdminUser]
    pagination_class=AdminProductsPagination

    def get_queryset(self):
        queryset = Products.objects.filter(is_deleted=False).order_by('-created_at')
        search_value = self.request.query_params.get("search")
        if search_value:
            queryset = queryset.filter(
                Q(brand__icontains=search_value) | Q(category__category__icontains=search_value)
            )

        else:
            queryset = queryset.order_by("-created_at")  # Default: newest first

        return queryset
    
class AdminCategoryView(APIView):
    permission_classes =[IsAdminUser]
    def get(self,request):
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = ProductCategorySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'category added successfully'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminProductAddView(APIView):
    permission_classes=[IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    def post(self,request):
        serializerr = ProductSerializer(data = request.data,context={"request": request})

        if serializerr.is_valid():
            serializerr.save()
            return Response({"message": "Product added!"}, status=201)
        return Response(serializerr.errors, status=400)
    

class AdminProductEditView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, pk):
        try:
            product = Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product,context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self,request,pk):
        try:
            product= Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            return Response({'error':'product cannot find'},status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product,data=request.data,partial =True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'product edited successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminProductDeleteView(APIView):
    permission_classes=[IsAdminUser]
    def delete(self,request,pk):
        try:
            products=Products.objects.get(pk=pk)
            products.is_deleted=True
            products.save()
        except Products.DoesNotExist:
            return Response({'error':'couldn\'t get the product'},status=status.HTTP_404_NOT_FOUND)
        
        return Response({'message':'product removed'},status=status.HTTP_200_OK)

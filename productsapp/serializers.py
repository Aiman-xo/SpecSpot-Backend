from rest_framework import serializers
from .models import ProductCategory,Products

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "category"]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source="category", read_only=True)
    # image = serializers.ImageField(use_url=True)
    image=serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields=[
            'id',
            'brand',
            'model',
            'image',
            'category',
            'category_name',
            'frame_material',
            'lens_type',
            "quantity",
            "in_stock",
            "price",
            "created_at",
        ]

    def get_image(self,obj):
        if obj.image:
            return obj.image.url
        return None
    
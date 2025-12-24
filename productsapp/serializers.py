from rest_framework import serializers
from .models import ProductCategory,Products

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "category"]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source="category", read_only=True)
    image = serializers.ImageField(required = False)
    #image=serializers.SerializerMethodField()

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if instance.image and request:
            data["image"] = request.build_absolute_uri(instance.image.url)

        return data
    

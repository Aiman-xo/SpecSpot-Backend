from .models import Wishlist
from productsapp.serializers import ProductSerializer
from rest_framework.serializers import ModelSerializer

class WishlistSerializer(ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = Wishlist
        fields =['id','product']
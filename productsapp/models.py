from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage

# Create your models here.


class ProductCategory(models.Model):
    category = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.category
    
     
class Products(models.Model):
    brand = models.CharField(max_length=255)
    image = models.ImageField(storage=MediaCloudinaryStorage(),upload_to="products/", null=True, blank=True)
    model = models.CharField(max_length=255)
    category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE)
    frame_material = models.CharField(max_length=255)
    lens_type = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_deleted = models.BooleanField(default=False,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model}"
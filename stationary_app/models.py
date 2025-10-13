from django.db import models
from django.contrib.auth.models import User


    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
        
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey("Category",on_delete=models.CASCADE, null=True,blank=True)
    company = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="GST rate in %")
    description = models.TextField()
    image = models.ImageField(upload_to="products/")

    def cgst_amount(self):
        return (self.price * (self.gst_rate / 2)) / 100

    def sgst_amount(self):
        return (self.price * (self.gst_rate / 2)) / 100

    def total_gst(self):
        return (self.price * self.gst_rate) / 100

    def total_price(self):
        return self.price + self.total_gst()

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"
    
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.product.name
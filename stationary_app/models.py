from django.db import models
from django.contrib.auth.models import User


    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('category', 'name')
        verbose_name_plural = "SubCategories"

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
class SubSubCategory(models.Model):
    subcategory = models.ForeignKey(SubCategory, related_name='subsubcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('subcategory','name')
        verbose_name_plural = "SubSubCategory"

        def __str__(self):
            return f"{self.subcategory.name} - {self.name}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    subsubcategory = models.ForeignKey(SubSubCategory, on_delete=models.CASCADE, null=True, blank=True)
    company = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, help_text="GST rate in %")
    description = models.TextField()
    image = models.ImageField(upload_to="products/")
    stock = models.PositiveIntegerField(default=0)

    @property
    def is_in_stock(self):
        return self.stock >0

    @property
    def category(self):
        """Returns the Category of the product via its SubCategory."""
        if self.subsubcategory:
            return self.subsubcategory.subcategory.category
        return None
    
    @property
    def subcategory(self):
        if self.subsubcategory:
            return self.subsubcategory.subcategory
        return None

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
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=250)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50) 
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Order {self.id} by {self.user.username}'
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'{self.product.name} ({self.quantity})'
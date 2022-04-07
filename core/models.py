from django.db import models
from django.contrib.auth.models import User

class AutoField(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Product(AutoField):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='images/products/', blank=True)
    def __str__(self):
        return self.name

class Product_size(AutoField):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=255)
    price = models.FloatField()
    stripe_price_id = models.CharField(max_length=255,null=True,blank=True)

    class Meta:
        unique_together = ('product', 'size')
        
    def __str__(self):
        return self.size

class CartItem(AutoField):
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product_size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    subtotal_price = models.FloatField(default=999999)
    def __str__(self):
        return f"{self.product.product.name} - {self.quantity} x {self.product.price}"

class Order(AutoField):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('payment_pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('shipping', 'Shipping'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField(null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255,null=True)
    phone = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    lat = models.FloatField(null=True,blank=True)
    lng = models.FloatField(null=True,blank=True)
    payment_method = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, default='pending', choices=STATUS_CHOICES)
    order_note = models.TextField(null=True,blank=True)
    stripe_session_id = models.CharField(max_length=255,null=True, blank=True)
    stripe_checkout_url = models.CharField(max_length=400,null=True, blank=True)
    def get_items(self):
        return self.orderitem_set.all()

    def __str__(self):
        return f"{self.user.username} - {self.total_price}"

class OrderItem(AutoField):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product_size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    subtotal_price = models.FloatField(default=999999)
    def __str__(self):
        return f"{self.product.product.name}\nSize:"

# Create your models here.

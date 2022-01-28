from django.contrib import admin
from .models import Product,Product_size,Order,OrderItem
from django.contrib.contenttypes.admin import GenericTabularInline
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description', 'image')
    list_filter = ('name', 'price', 'description', 'image')
    search_fields = ('name', 'price', 'description', 'image')

class Product_sizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'price')
    list_filter = ('product', 'size', 'price')
    search_fields = ('product', 'size', 'price')

class OrderItem(admin.TabularInline):
    model = OrderItem
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at','payment_method')
    list_filter = ('status',)
    inlines = (OrderItem,)
admin.site.register(Product, ProductAdmin)
admin.site.register(Product_size, Product_sizeAdmin)
admin.site.register(Order,OrderAdmin)
# # Register your models here.

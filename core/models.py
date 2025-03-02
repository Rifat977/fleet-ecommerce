from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.text import slugify
import random, string

import barcode
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile
from io import BytesIO

from django.db.models import Sum

class User(AbstractUser): 
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('sales_rep', 'Sales Representative'),
        ('customer', 'Customer'),
    )
    is_verified = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    street_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set", 
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set", 
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def is_admin(self):
        return self.role == 'admin'

    def is_sales_rep(self):
        return self.role == 'sales_rep'

    def is_customer(self):
        return self.role == 'customer'

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "                    All Users"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    class Meta:
        verbose_name = "Admins"
        verbose_name_plural = "                   Admins"

class SalesRepresentativeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_rep_profile')

    class Meta:
        verbose_name = "Sales Representives"
        verbose_name_plural = "                  Sales Representives"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    class Meta:
        verbose_name = "Customers"
        verbose_name_plural = "                 Customers"

class Cupon(models.Model):
    code = models.CharField(max_length=255, unique=True)
    discount = models.IntegerField(default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_usage = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name = "Cupon"
        verbose_name_plural = "                Coupons"

class CuponApplied(models.Model):
    cupon = models.ForeignKey(Cupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.cupon.code}"
    
    class Meta:
        verbose_name = "Cupon Applied"
        verbose_name_plural = "               Coupons Applied"


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    logo = models.ImageField(upload_to="category/image", blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="subcategories"
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "             Categories"


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "            Tags"


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True) 

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "           Sizes"
        ordering = ['name']


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True) 
    hex_code = models.CharField(max_length=7, unique=True, help_text="Hex color code, e.g., #FF5733")

    def __str__(self):
        return f"{self.name} ({self.hex_code})"

    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "           Colors"
        ordering = ['name']


class Product(models.Model):
    # Basic product details
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()
    is_featured = models.BooleanField(default=False)
    
    # Price and discount
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Discount in percentage
    
    # Barcode and stock
    barcode = models.ImageField(upload_to="products/barcodes", blank=True, null=True)  # Barcode as image
    stock_quantity = models.PositiveIntegerField()

    # Product attributes
    size = models.ManyToManyField(Size, blank=True)
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True, null=True)

    # Relations
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True)

    # Media
    image = models.ImageField(upload_to="products/images", blank=True, null=True)

    sku = models.CharField(max_length=8, unique=True, blank=True, null=True)

    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def stock_status(self):
        if self.stock_quantity > 10:
            return "In Stock"
        elif self.stock_quantity > 0:
            return "Low Stock"
        return "Out of Stock"

    @property
    def discounted_price(self):
        return self.price * (1 - self.discount / 100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """ Ensure SKU and barcode are generated correctly before saving. """
        if not self.slug:
            self.slug = slugify(self.name)

        if not self.sku:
            self.sku = self.generate_unique_sku()

        super().save(*args, **kwargs)  # First, save the object to ensure `self.id` exists.

        if not self.barcode:  # Generate barcode only if it doesn't exist
            self.generate_barcode()

    def generate_unique_sku(self):
        """ Generate a unique SKU with 8 uppercase letters and numbers. """
        while True:
            sku = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Product.objects.filter(sku=sku).exists():
                return sku

    def generate_barcode(self):
        if self.id and self.category_id and self.sku:
            category_code = str(self.category_id).zfill(2) 
            barcode_data = f"{self.id}-{category_code}-{self.sku}"

            code128 = barcode.get_barcode_class('code128')
            barcode_obj = code128(barcode_data, writer=ImageWriter())

            buffer = BytesIO()
            barcode_obj.write(buffer)
            filename = f"barcode_{self.sku}.png"

            self.barcode.save(filename, ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=['barcode'])

    def update_stock_quantity(self):
        total_stock = self.gallery.aggregate(total=Sum('stock'))['total'] or 0
        self.stock_quantity = total_stock
        self.save(update_fields=['stock_quantity'])


    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "          Products"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="images")  
    image = models.ImageField(upload_to="products/gallery")
    stock = models.PositiveIntegerField(default=0)
    alt_text = models.CharField(max_length=255, blank=True, null=True)  # For SEO purposes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = "Product Image"
        verbose_name_plural = "         Product Images"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=255)  # e.g., Size, Color
    value = models.CharField(max_length=255)  # e.g., Medium, Red

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

    class Meta:
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"


class Cart(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "        Carts"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.discounted_price

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "       Cart Items"


class Order(models.Model):
    ORDER_STATUSES = [
        ("pending", "Pending"),
        ("confirmed", "Order Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
    ]

    PAYMENT_METHODS = [
        ("cod", "Cash on Delivery"),
        ("bank_transfer", "Bank Transfer"),
        ("card", "Card"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    # user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="orders")
    # order_status = models.CharField(max_length=20, choices=ORDER_STATUSES, default="pending")
    # subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    # total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Discount in amount")
    # tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Tax in amount")
    # shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Shipping cost in amount")
    # shipping_address = models.TextField()
    # payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cod")
    # payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="orders")
    order_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    order_status = models.CharField(max_length=20, choices=ORDER_STATUSES, default="pending")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Cupon, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Discount in amount")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Tax in amount")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Shipping cost in amount")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    shipping_address = models.TextField()

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cod")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        super().save(*args, **kwargs)

    def generate_order_id(self):
        return f"FINCH-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "      Orders"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase

    def total_price(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"Order {self.order.id} - {self.product.name}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "     Order Items"


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=100, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    pdf = models.FileField(upload_to="invoices/", blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.order.id}"

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "    Invoices"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    class Meta:
        verbose_name = "Wishlist"
        verbose_name_plural = "   Wishlists"


class ProductAnalytics(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="analytics")
    views = models.PositiveIntegerField(default=0)
    purchases = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} Analytics"

    class Meta:
        verbose_name = "Product Analytics"
        verbose_name_plural = "  Product Analytics"












from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=ProductImage)
@receiver(post_delete, sender=ProductImage)
def update_product_stock(sender, instance, **kwargs):
    instance.product.update_stock_quantity()

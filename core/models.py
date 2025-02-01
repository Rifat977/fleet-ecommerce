from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('sales_rep', 'Sales Representative'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

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
        verbose_name_plural = "                  All Users"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    class Meta:
        verbose_name = "Admins"
        verbose_name_plural = "                 Admins"

class SalesRepresentativeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_rep_profile')

    class Meta:
        verbose_name = "Sales Representives"
        verbose_name_plural = "                Sales Representives"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')

    class Meta:
        verbose_name = "Customers"
        verbose_name_plural = "               Customers"

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="category/image", blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="subcategories"
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "             Categories"


class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "            Tags"


class Brand(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "           Brands"


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Discount in percentage
    barcode = models.CharField(max_length=100, unique=True)
    colors = models.JSONField(blank=True, null=True)  # List of available colors
    seo_title = models.CharField(max_length=255, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    seo_keywords = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    stock_quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to="products/images", blank=True, null=True)
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

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "          Products"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="products/gallery")
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

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "      Orders"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
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


class POS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pos")
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Discount percentage on total sale
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Tax percentage
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("cash", "Cash"),
            ("credit_card", "Credit Card"),
            ("debit_card", "Debit Card"),
            ("online", "Online Payment"),
        ],
        default="cash",
    )
    notes = models.TextField(blank=True, null=True)  # Additional notes about the sale

    @property
    def net_total(self):
        """Calculate the total after applying discount and adding tax."""
        discount_amount = (self.total_amount * self.discount) / 100
        taxable_amount = self.total_amount - discount_amount
        tax_amount = (taxable_amount * self.tax) / 100
        return taxable_amount + tax_amount

    def __str__(self):
        return f"POS Sale - {self.id} by {self.user.username}"

    class Meta:
        verbose_name = "POS Sale"
        verbose_name_plural = " POS Sales"


class POSItem(models.Model):
    pos = models.ForeignKey(POS, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Discount on item in percentage
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        """Calculate the total price for the item after discount."""
        discount_amount = (self.sale_price * self.discount) / 100
        self.total_price = (self.sale_price - discount_amount) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for POS {self.pos.id}"

    class Meta:
        verbose_name = "POS Item"
        verbose_name_plural = "POS Items"

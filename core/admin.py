from django.contrib.auth.models import User
from django.contrib import admin
admin.site.unregister(User)


from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(AdminProfile)
class CustomUserAdmin(ModelAdmin):
    list_display = ('user',)

@admin.register(SalesRepresentativeProfile)
class CustomUserAdmin(ModelAdmin):
    list_display = ('user',)

@admin.register(CustomerProfile)
class CustomUserAdmin(ModelAdmin):
    list_display = ('user',)

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget()},
    }

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("name", "price", "stock_quantity", "category", "brand", "discounted_price")
    list_filter = ("category", "brand", "created_at")
    search_fields = ("name", "slug", "barcode")
    prepopulated_fields = {"slug": ("name",)}
    formfield_overrides = {
        models.JSONField: {"widget": ArrayWidget()},
        models.TextField: {"widget": WysiwygWidget()},
    }

@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    list_display = ("product", "name", "value")
    search_fields = ("product__name", "name", "value")

@admin.register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("product", "image", "alt_text")
    search_fields = ("product__name", "alt_text")

@admin.register(Wishlist)
class WishlistAdmin(ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")

@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username",)

@admin.register(CartItem)
class CartItemAdmin(ModelAdmin):
    list_display = ("cart", "product", "quantity", "total_price")
    search_fields = ("cart__user__username", "product__name")

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("user", "status", "total_price", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("user__username",)

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ("order", "product", "quantity", "price_at_purchase", "total_price")
    search_fields = ("order__user__username", "product__name")

@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ("invoice_number", "order", "issued_date", "due_date")
    search_fields = ("invoice_number", "order__user__username")

@admin.register(POS)
class POSAdmin(ModelAdmin):
    list_display = ("user", "sale_date", "total_amount", "discount", "tax", "net_total", "payment_method")
    list_filter = ("payment_method", "sale_date")
    search_fields = ("user__username",)

@admin.register(POSItem)
class POSItemAdmin(ModelAdmin):
    list_display = ("pos", "product", "quantity", "sale_price", "discount", "total_price")
    search_fields = ("pos__user__username", "product__name")

@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(ModelAdmin):
    list_display = ("product", "views", "purchases")
    search_fields = ("product__name",)

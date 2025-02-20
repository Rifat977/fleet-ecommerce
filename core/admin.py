from django.contrib.auth.models import User
from django.contrib import admin
# admin.site.unregister(User)


from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget
from django.db import models
from django.contrib.auth.admin import UserAdmin
from .models import *
import json


@admin.register(User)
class CustomUserAdmin(ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified', 'role')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
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

@admin.register(Size)
class SizeAdmin(ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Color)
class ColorAdmin(ModelAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name', 'hex_code')
    ordering = ('name',)

# @admin.register(Product)
# class ProductAdmin(ModelAdmin):
#     list_display = ("name", "price", "stock_quantity", "category", "brand", "discounted_price")
#     list_filter = ("category", "brand", "created_at")
#     search_fields = ("name", "slug", "barcode")
#     prepopulated_fields = {"slug": ("name",)}
#     formfield_overrides = {
#         models.JSONField: {"widget": ArrayWidget()},
#         models.TextField: {"widget": WysiwygWidget()},
#     }

# @admin.register(ProductVariant)
# class ProductVariantAdmin(ModelAdmin):
#     list_display = ("product", "name", "value")
#     search_fields = ("product__name", "name", "value")

# Inline admin for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  
    fields = ('image', 'alt_text') 


class ProductAdmin(ModelAdmin):
    list_display = ('name', 'price', 'sku', 'is_featured', 'stock_quantity', 'category', 'created_at')
    search_fields = ('name', 'sku', 'barcode', 'category__name')
    list_filter = ('category', 'created_at')

    inlines = [ProductImageInline]

    def get_fieldsets(self, request, obj=None):
        """ Exclude 'barcode' and 'sku' fields when adding a new product. """
        if obj is None:  # If adding a new product
            return (
                (None, {
                    'fields': ('name', 'slug', 'description', 'is_featured', 'price', 'discount', 'stock_quantity')
                }),
                ('SEO', {
                    'fields': ('seo_title', 'seo_description', 'seo_keywords')
                }),
                ('Relations', {
                    'fields': ('category', 'tags', 'color', 'size')
                }),
                ('Media', {
                    'fields': ('image',)
                }),
            )
        return super().get_fieldsets(request, obj)  # Show all fields when editing

    formfield_overrides = {
        models.TextField: {'widget': WysiwygWidget},  
        models.JSONField: {'widget': ArrayWidget},   
    }

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)


# @admin.register(ProductImage)
# class ProductImageAdmin(ModelAdmin):
#     list_display = ("product", "image", "alt_text")
#     search_fields = ("product__name", "alt_text")



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

@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(ModelAdmin):
    list_display = ("product", "views", "purchases")
    search_fields = ("product__name",)


@admin.register(Cupon)
class CuponAdmin(ModelAdmin):
    list_display = ("code", "discount", "is_active", "created_at", "updated_at")
    search_fields = ("code",)

@admin.register(CuponApplied)
class CuponAppliedAdmin(ModelAdmin):
    list_display = ("user", "cupon", "created_at")
    search_fields = ("user__username", "cupon__code")



# serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import *

User = get_user_model()


# User Authentication and authrorizaiton

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'phone_number')

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', ''),
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  
        return token

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role']


# Products

class ProductSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="id", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "_id", "name", "slug", "is_featured", "price", 
            "stock_quantity",
            "category_name", 'currency', "image", "created_at"
        ]

    def get_currency(self, obj):
        return "$"

class AllProductSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="id", read_only=True)
    category_name = serializers.CharField(source="category.name")
    currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            "_id", "name", "slug", "is_featured", "price", 
            "stock_quantity",
            "category_name", 'currency', "image", "created_at"
        ]
    
    def get_currency(self, obj):
        return "$"
    
    def get_images(self, obj):
        return [obj.image.url] if obj.image else []  # Assuming a single main image, modify if multiple

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "created_at"]

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "hex_code"]

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ["id", "name"]

class ProductDetailsSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name") 
    color = ColorSerializer(many=True, read_only=True)  
    size = SizeSerializer(many=True, read_only=True) 
    gallery = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "is_featured",
            "price",
            "discount",
            "discounted_price",
            "barcode",
            "stock_quantity",
            "stock_status",
            "color", 
            "size",
            "category_name",
            "seo_title",
            "seo_description",
            "seo_keywords",
            "category",
            "tags",
            'currency',
            "image", 
            "gallery", 
            "created_at",
            "updated_at",
        ]
    def get_currency(self, obj):
        return "$"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "logo", "parent", "description"]


class CuponAppliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuponApplied
        fields = "__all__"
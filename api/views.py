from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from core.models import Product, Cupon, CuponApplied
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, filters, pagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.generics import RetrieveAPIView

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
from django.core.exceptions import ObjectDoesNotExist


User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return JsonResponse({"detail": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        authenticated_user = authenticate(request, username=user.username, password=password)  

        if authenticated_user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_data = CustomUserSerializer(user).data  

            return JsonResponse({
                "access": access_token,
                "refresh": str(refresh),
                "user": user_data
            }, status=status.HTTP_200_OK)

        return JsonResponse({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

    except User.DoesNotExist:
        return JsonResponse({"detail": "Invalid email or password"}, status=status.HTTP_404_NOT_FOUND)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class VerifyTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "message": "Token is valid",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }, status=status.HTTP_200_OK)



# Products 
class ProductPagination(pagination.PageNumberPagination):
    page_size = 40  # Adjust page size as needed
    page_size_query_param = "page_size"
    max_page_size = 100

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "created_at", "stock_quantity"]
    ordering = ["-created_at"]  # Default ordering

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data).data  # Get default paginated response
            response["total_pages"] = self.paginator.page.paginator.num_pages  # Add total_pages
            return Response(response)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AllProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("id")  # Order by ID to maintain order
    serializer_class = AllProductSerializer
    pagination_class = ProductPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "total_pages": self.paginator.page.paginator.num_pages,
            "count": self.paginator.page.paginator.count,
            "next": self.paginator.get_next_link(),
            "previous": self.paginator.get_previous_link(),
            "results": serializer.data
        })

class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.prefetch_related("gallery").all()
    serializer_class = ProductDetailsSerializer
    lookup_field = "id" 

    def get(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def apply_cupon(request):
    if request.method == 'POST':
        try:
            cupon_code = request.POST.get("cupon_code")
            total_amount = request.POST.get("total_amount")
            customer = request.POST.get("customer")
            try:
                customer = User.objects.get(id=customer)
            except User.DoesNotExist:
                return JsonResponse({"error": "Customer not found"}, status=status.HTTP_400_BAD_REQUEST)
            total_amount = float(total_amount)

            print(cupon_code, total_amount, customer)

            cupon = Cupon.objects.get(code=cupon_code, is_active=True)

            if total_amount < cupon.min_order_amount:
                return JsonResponse({"error": f"Total amount is less than the minimum order amount: {cupon.min_order_amount}"}, status=status.HTTP_400_BAD_REQUEST)
            if cupon.max_usage <= CuponApplied.objects.filter(cupon=cupon, user=customer).count():
                return JsonResponse({"error": f"You have reached the maximum usage limit for this coupon"}, status=status.HTTP_400_BAD_REQUEST)
            
            new_total_amount = total_amount - (total_amount * cupon.discount / 100)

            # CuponApplied.objects.create(
            #     cupon=cupon,
            #     user=customer,
            # )
            
            return JsonResponse({"message": f"Cupon applied successfully. You got {cupon.discount}% off", "total_amount": new_total_amount}, status=status.HTTP_200_OK)
        except Cupon.DoesNotExist:
            return JsonResponse({"error": "Invalid coupon code"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return JsonResponse({"error": "Customer not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_product_stock(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "error": "Invalid request method."}, status=405)
    
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        color = data.get("color")
        color = Color.objects.get(hex_code=color)
        quantity = data.get("quantity")

        print(product_id, color, quantity)

        product = Product.objects.get(id=product_id)
        product_image = ProductImage.objects.get(product=product, color=color)
        if product_image.stock > 0 and product_image.stock >= quantity:
            return JsonResponse({"valid": True, "stock": product_image.stock}, status=200)
        elif product_image.stock > 0 and product_image.stock < quantity:
            return JsonResponse({"valid": False, "error": f"Only {product_image.stock} {product_image.color.name} {product_image.product.name} left in stock."})
        else:
            return JsonResponse({"valid": False, "error": "This color is out of stock."}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"valid": False, "error": "Product not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"valid": False, "error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"valid": False, "error": f"An unexpected error occurred: {str(e)}"}, status=500)
    
from setting.models import CompanySetting
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_company_setting(request):
    company_setting = CompanySetting.objects.first()
    serializer = CompanySettingSerializer(company_setting)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
# @permission_classes([AllowAny])
def place_order(request):
    if request.method != "POST":
        return JsonResponse({"valid": False, "error": "Invalid request method."}, status=405)

    data = json.loads(request.body)
    is_registered = data.get("is_registered")
    orders = data.get("orders")
    order_info = data.get("order_info")
    billing_address = data.get("billing_address")
    coupon = data.get("coupon")

    if is_registered:
        if not request.user.is_authenticated:
            return JsonResponse({"valid": False, "error": "User not authenticated."}, status=401)
        user = request.user
    else:
        serializer = UserRegistrationSerializer(data=billing_address)
        if serializer.is_valid():
            serializer.save()
        else:
            # return errors properly
            error_messages = []
            for field, errors in serializer.errors.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")
            return JsonResponse({"valid": False, "error": error_messages})
    
    #update billing details for user profile except email password
    user.first_name = billing_address.get("first_name")
    user.last_name = billing_address.get("last_name")
    user.phone_number = billing_address.get("phone_number")
    user.street_address = billing_address.get("street_address")
    user.city = billing_address.get("city")
    user.state = billing_address.get("state")
    user.save()
    
    # create order and order items. Also Validate coupon, tax, discount, product price, shipping fee, total amount
    company_setting = CompanySetting.objects.first()
    tax = company_setting.tax
    shipping_fee = company_setting.shipping_fee
    
    # validate product price
    srv_subtotal = 0
    for order in orders:
        product = Product.objects.get(id=order.get("product_id"))
        srv_subtotal += product.price * order.get("quantity")

    # validate coupon
    if coupon:
        try:
            cupon_instance = Cupon.objects.get(code=coupon, is_active=True)
        except Cupon.DoesNotExist:
            return JsonResponse({"error": "Invalid coupon code"})

        if srv_subtotal < cupon_instance.min_order_amount:
            return JsonResponse({"error": f"Total amount is less than the minimum order amount: {cupon_instance.min_order_amount}"})
        if cupon_instance.max_usage <= CuponApplied.objects.filter(cupon=cupon_instance, user=user).count():
            return JsonResponse({"error": f"You have reached the maximum usage limit for this coupon"})

    srv_total_price = srv_subtotal - (srv_subtotal * cupon_instance.discount / 100)
    srv_tax = srv_total_price * tax / 100
    srv_shipping_cost = shipping_fee
    srv_total_price = srv_total_price + srv_tax + srv_shipping_cost
    
    order_info = Order.objects.create(
        user=user,
        subtotal=srv_subtotal,
        coupon=cupon_instance,
        discount=cupon_instance.discount if coupon else 0,
        tax=srv_tax,
        shipping_cost=srv_shipping_cost,
        total_price=srv_total_price,
        shipping_address=order_info.get("shipping_address"),
        payment_method=order_info.get("payment_method"),
    )

    if order_info:
        CuponApplied.objects.create(cupon=cupon_instance, user=user)
    
        order_items = []
        for order in orders:
            product = Product.objects.get(id=order.get("product_id"))
            color = Color.objects.get(hex_code=order.get("color"))
            size = Size.objects.get(name=order.get("size"))
            product_image = ProductImage.objects.get(product=product, color=color)
            order_items.append(OrderItem.objects.create(
                order=order_info,
                product=product,
                quantity=order.get("quantity"),
                color=product_image.color,
                size=size,
                price_at_purchase=product.price,
            ))

    return JsonResponse({"valid": True, "message": "Order placed successfully. Your order id is " + order_info.order_id}, status=200)
    
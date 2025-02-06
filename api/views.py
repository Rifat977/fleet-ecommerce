from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from core.models import Product
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, filters, pagination
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from rest_framework.generics import RetrieveAPIView


User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"detail": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        authenticated_user = authenticate(request, username=user.username, password=password)  

        if authenticated_user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            user_data = CustomUserSerializer(user).data  

            return Response({
                "access": access_token,
                "refresh": str(refresh),
                "user": user_data
            }, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

    except User.DoesNotExist:
        return Response({"detail": "Invalid email or password"}, status=status.HTTP_404_NOT_FOUND)




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
from django.urls import path
from .views import *

app_name = "api"

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),

    path("filter-products/", ProductListView.as_view(), name="product-list"),
    path('products/', AllProductListView.as_view(), name='all-products'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),

    path('category/', CategoryListView.as_view(), name='category-list'),
]


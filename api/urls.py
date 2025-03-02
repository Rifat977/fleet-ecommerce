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

    path('apply-cupon/', apply_cupon, name='apply-cupon'),
    path('verify-product-stock/', verify_product_stock, name='verify-product-stock'),

    path('get-company-setting/', get_company_setting, name='get-company-setting'),
    path('place-order/', place_order, name='place-order'),
]


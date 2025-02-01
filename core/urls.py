from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('products/', views.product, name="product"),
    path('add-product/', views.add_product, name="add_product"),
    path('category/', views.category, name="category"),
]

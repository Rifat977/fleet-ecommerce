from django.shortcuts import render
from .decorators import admin_required, sales_rep_required, customer_required

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')

def product(request):
    return render(request, 'product.html')

def add_product(request):
    return render(request, 'add-product.html')

def category(request):
    return render(request, 'category.html')
from django.shortcuts import render, get_object_or_404, redirect
from .decorators import admin_required, sales_rep_required, customer_required
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse


# Create your views here.
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_admin():
                return redirect('core:dashboard')
            elif user.is_sales_rep():
                pass
                # return redirect('sales_rep_dashboard')
            elif user.is_customer():
                pass
                return redirect('core:login')
    return render(request, 'account/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:login')

@admin_required
def dashboard(request):
    return render(request, 'dashboard.html')

def product(request):
    return render(request, 'product.html')

def category(request):
    category_list = Category.objects.all().order_by('-id')
    paginator = Paginator(category_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category.html', {'page_obj': page_obj})

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

def pos(request):
    # Get all categories and customers
    categories = Category.objects.all()
    customers = User.objects.filter(role='customer')

    # Handle the AJAX request
    if request.method == "POST":
        category_filter = request.POST.get('category', '')
        customer_filter = request.POST.get('customer', '')
        search_query = request.POST.get('search', '')

        # Filter products based on category, customer, and search query
        products = Product.objects.all()

        if category_filter:
            products = products.filter(category__id=category_filter)
        if customer_filter:
            products = products.filter(customer__id=customer_filter)
        if search_query:
            products = products.filter(name__icontains=search_query)

        # Paginate filtered products (12 per page)
        paginator = Paginator(products, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Prepare data for the response
        product_data = []
        for product in page_obj:
            product_data.append({
                'id': product.id,
                'name': product.name,
                'category': product.category.name,
                'price': product.price,
                'stock_quantity': product.stock_quantity,
                'image_url': product.image.url,
                'colors': [color.hex_code for color in product.color.all()],
                'sizes': [size.name for size in product.size.all()]
            })

        # Return the filtered products and pagination data in JSON format
        return JsonResponse({
            'products': product_data,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'num_pages': page_obj.paginator.num_pages,
            'current_page': page_obj.number,
        })

    # Default rendering (no AJAX request)
    products = Product.objects.all()
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'customers': customers,
    }
    return render(request, 'pos.html', context)


def product(request):
    return render(request, 'product.html')

def category(request):
    category_list = Category.objects.all().order_by('-id')
    paginator = Paginator(category_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'category.html', {'page_obj': page_obj})

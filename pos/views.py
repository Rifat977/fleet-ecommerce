from django.shortcuts import render
from core.models import *
from django.core.paginator import Paginator
from django.http import JsonResponse
from pos.models import POS, PAYMENT_METHOD

from setting.models import CompanySetting

# Create your views here.
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
        # if customer_filter:
        #     products = products.filter(customer__id=customer_filter)
        # if search_query:
        #     products = products.filter(name__icontains=search_query)

        if search_query:
            products = products.filter(models.Q(name__icontains=search_query) | models.Q(sku__icontains=search_query))


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
                'sizes': [size.name for size in product.size.all()],
                'sku'  : product.sku
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
    products = Product.objects.all().order_by('-id')
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    company_setting = CompanySetting.objects.first()
    payment_methods = PAYMENT_METHOD

    context = {
        'products': page_obj,
        'categories': categories,
        'customers': customers,
        'company_setting': company_setting,
        'payment_methods': payment_methods,
    }
    return render(request, 'pos.html', context)

def checkout(request):
    print(request.POST)
    pass


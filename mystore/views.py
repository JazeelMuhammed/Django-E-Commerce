from django.http import JsonResponse
from django.shortcuts import render
from store.models import Product
from django.views.generic import View, TemplateView
from django.template.loader import render_to_string

def home(request):
    products = Product.objects.all().filter(is_available=True)[:8]
    popular_products = Product.objects.all().filter(is_available=True, type='popular').order_by('?')
    trending_products = Product.objects.all().filter(is_available=True, type='trending').order_by('?')
    iconic_products = Product.objects.all().filter(is_available=True, type='iconic').order_by('id')[:4]
    total_iconic = Product.objects.all().filter(is_available=True, type='iconic').count()

    total_iconic = iconic_products.count()
    
    context = {
        'products': products,
        'popular_products': popular_products,
        'trending_products': trending_products,
        'iconic_products': iconic_products,
        'total_iconic': total_iconic,
    }
    return render(request, 'home.html', context)


class ProductsJsonListView(View):
    def get(self, *args, **kwargs):
        upper = kwargs.get('num_products')   # 8
        lower = upper - 4   # 0

        iconic_products = list(Product.objects.all().filter(is_available=True, type='iconic').values()[lower:upper])  # [0:8]
        iconic_products_size = len(Product.objects.all().filter(is_available=True, type='iconic'))
        max_iconic_size = True if upper >= iconic_products_size else False

        popular_products = list(Product.objects.all().filter(is_available=True, type='popular').values()[lower:upper])
        popular_products_size = len(Product.objects.all().filter(is_available=True, type='popular'))
        max_popular_size = True if upper >= popular_products_size else False
        
        return JsonResponse({'iconic_data': iconic_products, 'max_iconic_size': max_iconic_size}, safe=False)


        
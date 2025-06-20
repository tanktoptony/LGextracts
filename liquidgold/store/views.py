from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q

def product_list(request):
    query = request.GET.get('q', '')
    selected_category = request.GET.get('category', 'all')
    
    products = Product.objects.filter(in_stock=True)
    categories = Category.objects.all()
    
    if selected_category != 'all':
        products = products.filter(category__id=selected_category)
        
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        
    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query
    })

'''def product_list(request):
    products = Product.objects.all()
    
    return render(request, 'store/product_list.html', {'products': products})
'''

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})

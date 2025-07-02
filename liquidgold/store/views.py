import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Order, OrderItem

from django.shortcuts import render, get_object_or_404
from django.db.models import Q

# store/views.py (or accounts/views.py)
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log them in
            return redirect('product_menu')  # Redirect to your main store page
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


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

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, paid=False)
    item, created = OrderItem.objects.get_or_create(order=order, product=product)
    item.quantity += 1
    item.save()
    return JsonResponse({'message': 'Added to cart'})

@login_required
def view_order(request):
    order = Order.objects.filter(user=request.user, paid=False).first()
    return render(request, 'store/order.html', {'order': order})

@login_required
def create_checkout_session(request):
    order = Order.objects.filter(user=request.user, paid=False).first()
    if not order:
        return JsonResponse({'error': 'No active order'}, status=400)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    line_items = []

    for item in order.orderitem_set.all():
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://localhost:8000/success/',
        cancel_url='http://localhost:8000/cancel/',
    )

    return JsonResponse({'id': session.id})

def success(request):
    order = Order.objects.filter(user=request.user, paid=False).first()
    if order:
        order.paid = True
        order.save()
    return render(request, 'store/success.html')

def cancel(request):
    return render(request, 'store/cancel.html')

def spanish(request):
    return render(request, 'spanish.html')

def lottery(request):
    return render(request, 'lottery.html')

def warnings(request):
    return render(request, 'warnings.html')
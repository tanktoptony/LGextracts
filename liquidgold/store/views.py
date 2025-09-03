import stripe, os, random, string

from flask import Flask, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Order, OrderItem, PromoCode

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

# store/views.py (or accounts/views.py)
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login

from django.core.mail import send_mail

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

#@login_required
def add_to_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Use session to track guest cart
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(user=request.user, paid=False)
    else:
        order, created = Order.objects.get_or_create(session_key=session_key, user=None, paid=False)

    item, created = OrderItem.objects.get_or_create(order=order, product=product)
    if not created:
        item.quantity += 1
    item.save()
    return redirect('view_order')


def view_order(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, paid=False).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        order = Order.objects.filter(session_key=session_key, user=None, paid=False).first()

    total = 0
    if order:
        total = sum(item.quantity * item.product.price for item in order.orderitem_set.all())

    return render(request, 'store/order.html', {'order': order, 'total': total})


def update_quantity(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(
            OrderItem,
            id=item_id,
            order__user=request.user,
            order__paid=False
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        item = get_object_or_404(
            OrderItem,
            id=item_id,
            order__session_key=session_key,
            order__user=None,
            order__paid=False
        )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            item.quantity += 1
        elif action == 'decrease':
            item.quantity -= 1
            if item.quantity < 1:
                item.delete()
                return redirect('view_order')
        item.save()

    return redirect('view_order')


def remove_from_order(request, item_id):
    if request.user.is_authenticated:
        item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__paid=False)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        item = get_object_or_404(OrderItem, id=item_id, order__session_key=session_key, order__user=None, order__paid=False)

    item.delete()
    return redirect('view_order')


def get_order(request):
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(user=request.user, paid=False)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        order, created = Order.objects.get_or_create(session_key=session_key, paid=False)
    return order

@csrf_exempt
def create_checkout_session(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, paid=False).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        order = Order.objects.filter(session_key=session_key, user=None, paid=False).first()

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
        success_url='http://localhost:8000/store/success/',
        cancel_url='http://localhost:8000/store/cancel/',
    )

    return JsonResponse({'id': session.id})

    order = get_order(request)
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
        success_url='http://localhost:8000/store/success/',
        cancel_url='http://localhost:8000/store/cancel/',
    )

    return JsonResponse({'id': session.id})

def success(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, paid=False).first()
    else:
        session_key = request.session.session_key
        order = Order.objects.filter(session_key=session_key, user=None, paid=False).first()

    if order:
        order.paid = True
        order.save()

    return render(request, 'store/success.html')


def cancel(request):
    return render(request, 'store/cancel.html')

def spanish(request):
    return render(request, 'spanish.html')

from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

def promo_claim(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        prize = request.POST.get("prize")

        subject = "New Prize Claim"
        message = f"""
        A new prize claim has been submitted:

        Name: {name}
        Email: {email}
        Prize: {prize}
        """

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ["lgextracts@gmail.com"])

        return render(request, "store/promo_claim.html", {
            "success": True,
            "name": name,
            "prize": prize
        })

    # GET request — show form
    prize = request.GET.get("prize", "")
    return render(request, "store/promo_claim.html", {"prize": prize})

def lottery(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        prize = request.POST.get("prize")

        # Build email message
        subject = "New Lottery Entry"
        message = f"""
        A new lottery form was submitted:

        Name: {name}
        Email: {email}
        Prize: {prize}
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ["lgextracts@gmail.com"])

        return render(request, "store/lottery_result.html", {"success": True})

    return render(request, "store/lottery.html")
    return render(request, 'lottery.html')

def warnings(request):
    return render(request, 'warnings.html')

def about(request):
    return render(request, 'about.html')

app = Flask(__name__)

stripe.api_key = 'sk_test_o482215W7Ef1KfFUXLTXZ8kp'

@app.route('/create-checkout-session/', methods=['POST'])
def create_checkout_session(request):
  session = stripe.checkout.Session.create(
    line_items=[{
      'price_data': {
        'currency': 'usd',
        'product_data': {
          'name': 'T-shirt',
        },
        'unit_amount': 2000,
      },
      'quantity': 1,
    }],
    mode ='payment',
    success_url ='http://127.0.0.1:8000/success',
    cancel_url ='http://127.0.0.1:8000/cancel',
  )

  return redirect(session.url, code=303)

if __name__== '__main__':
    app.run(port=4242)
    

def lottery_view(request):
    win_chance = 0.25  # 25% chance to win

    # Use session to prevent repeat plays, optional
    if request.session.get('played_lottery'):
        return render(request, 'store/lottery_result.html', {
            'win': False,
            'code': None,
            'played': True
        })

    win = True
    code = None

    if win:
        # Generate unique 8-character code
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not PromoCode.objects.filter(code=code).exists():
                break

        PromoCode.objects.create(code=code, discount=100, used=False)

    # Optional: block replay until browser session is cleared
    request.session['played_lottery'] = True

    return render(request, 'store/lottery_result.html', {
        'win': win,
        'code': code,
        'played': True
    })

# Lottery Spin Page
def promo_wheel(request):
    request.session.setdefault("last_spin", None)
    return render(request, "lottery.html")

# Prize Claim Page (sends email)
def promo_claim(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get

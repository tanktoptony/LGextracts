from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from blog.models import Post, Comment
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage
from blog.forms import CommentForm, OrderForm, PrizeClaimForm

# Create your views here.
def home(request):
    return render(request, "blog/index.html")

def article_index(request):
    posts = Post.objects.all().order_by("-created_on")
    context = {
        "posts": posts,
    }
    return render(request, "blog/articles.html", context)

def blog_category(request, category):
    posts = Post.objects.filter(
        categories__name__contains=category
    ).order_by("-created_on")
    context = {
        "category": category,
        "posts": posts,
    }
    return render(request, "blog/category.html", context)

def blog_detail(request, pk):
    post = Post.objects.get(pk=pk)
    form = CommentForm()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author=form.cleaned_data["author"],
                body=form.cleaned_data["body"],
                post=post,
            )
            comment.save()

            return HttpResponseRedirect(request.path_info)
    comments = Comment.objects.filter(post=post)
    context = {
        "post": post,
        "comments": comments,
        "form": CommentForm(),
    }

    return render(request, "blog/detail.html", context)

def subscribe(request):
    if request.method == "POST":
        email = request.POST.get('email')
        # You could save it to a model or send to a 3rd-party API like Mailchimp
        messages.success(request, "Thanks for subscribing!")
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Lottery Forms

# (A) Spin page (QR can point here)
def promo_wheel(request):
    # optionally gate spins by session (1 spin/day)
    request.session.setdefault("last_spin", None)
    return render(request, "lottery.html")  # or "promo_spin.html" if you created a new file

# (B) Claim page (GET shows form with ?prize=..., POST sends email)
def promo_claim(request):
    initial_prize = request.GET.get("prize", "Hat")  # default fallback
    if request.method == "POST":
        form = PrizeClaimForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = f"[Spin&Win] Prize claim: {data['prize']} – {data['full_name']}"
            body = (
                f"Prize: {data['prize']}\n"
                f"Name: {data['full_name']}\n"
                f"Email: {data['email']}\n"
                f"Phone: {data.get('phone','')}\n"
                f"Address: {data.get('address','')}\n"
                f"Size: {data.get('size','N/A')}\n"
                f"Notes: {data.get('notes','')}\n"
            )
            to_addr = getattr(settings, "ORDERS_EMAIL_TO", settings.DEFAULT_FROM_EMAIL)
            EmailMessage(subject, body, to=[to_addr]).send(fail_silently=False)
            return render(request, "promo_claim.html", {"submitted": True})
    else:
        form = PrizeClaimForm(initial={"prize": initial_prize})
    return render(request, "promo_claim.html", {"form": form, "prize": initial_prize})

# (C) Order form (under Shop)
def order_form(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            subject = f"[Shop Order] {data['full_name']}"
            body = (
                f"Name: {data['full_name']}\n"
                f"Email: {data['email']}\n"
                f"Phone: {data.get('phone','')}\n"
                f"Items:\n{data['items']}\n\n"
                f"Notes:\n{data.get('notes','')}\n"
            )
            to_addr = getattr(settings, "ORDERS_EMAIL_TO", settings.DEFAULT_FROM_EMAIL)
            EmailMessage(subject, body, to=[to_addr]).send(fail_silently=False)
            return render(request, "order_form.html", {"submitted": True})
    else:
        form = OrderForm()
    return render(request, "order_form.html", {"form": form})

# (D) Optional: Serve a QR image that links to the spin page
def promo_wheel_qr(request):
    """
    Requires 'qrcode' and 'Pillow':
      pip install qrcode[pil]
    """
    import qrcode
    from io import BytesIO
    from django.utils.http import urlencode

    url = request.build_absolute_uri(reverse("promo_wheel"))
    img = qrcode.make(url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")

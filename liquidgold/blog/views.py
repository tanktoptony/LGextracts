from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from blog.models import Post, Comment
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from blog.forms import CommentForm, OrderForm

# Home Page
def home(request):
    return render(request, "blog/index.html")

# Blog Pages
def article_index(request):
    posts = Post.objects.all().order_by("-created_on")
    return render(request, "blog/articles.html", {"posts": posts})

def blog_category(request, category):
    posts = Post.objects.filter(
        categories__name__contains=category
    ).order_by("-created_on")
    return render(request, "blog/category.html", {"category": category, "posts": posts})

def blog_detail(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                author=form.cleaned_data["author"],
                body=form.cleaned_data["body"],
                post=post,
            )
            return HttpResponseRedirect(request.path_info)
    comments = Comment.objects.filter(post=post)
    return render(request, "blog/detail.html", {
        "post": post,
        "comments": comments,
        "form": CommentForm(),
    })

# Subscribe
def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        messages.success(request, "Thanks for subscribing!")
    return redirect(request.META.get("HTTP_REFERER", "/"))

# Lottery Spin Page
def promo_wheel(request):
    request.session.setdefault("last_spin", None)
    return render(request, "lottery.html")

# Prize Claim Page (sends email)
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

    # Handle GET requests
    prize = request.GET.get("prize", "")
    return render(request, "store/promo_claim.html", {"prize": prize})

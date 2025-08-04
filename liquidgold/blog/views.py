from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from blog.models import Post, Comment
from blog.forms import CommentForm

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
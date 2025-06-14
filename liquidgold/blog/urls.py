from django.urls import path
from . import views

urlpatterns = [
    path("", views.blog_index, name="blog_index"), ### you can edit here to make a different page the home page
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("category/<category>/", views.blog_category, name="blog_category"),
    
]
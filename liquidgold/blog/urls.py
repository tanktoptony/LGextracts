from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("articles", views.article_index, name="article_index"), ### you can edit here to make a different page the home page
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("category/<category>/", views.blog_category, name="blog_category"),
    path('subscribe/', views.subscribe, name='subscribe'),
    
]
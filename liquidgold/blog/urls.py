from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("articles", views.article_index, name="article_index"), ### you can edit here to make a different page the home page
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("category/<category>/", views.blog_category, name="blog_category"),
    path('subscribe/', views.subscribe, name='subscribe'),
    path("promo/wheel/", views.promo_wheel, name="promo_wheel"),
    path("promo/claim/", views.promo_claim, name="promo_claim"),
    #path("promo/wheel-qr.png", views.promo_wheel_qr, name="promo_wheel_qr"),
    #path("shop/order-form/", views.order_form, name="order_form"),
]
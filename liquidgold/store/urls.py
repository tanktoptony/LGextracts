from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.product_list, name='product_menu'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('add-to-order/<int:product_id>/', views.add_to_order, name='add_to_order'),
    path('order/', views.view_order, name='view_order'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('remove-from-order/<int:item_id>/', views.remove_from_order, name='remove_from_order'),
    path('update-quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('about/', views.about, name='about'),
    ### path('spanish/', views.spanish, name='spanish'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


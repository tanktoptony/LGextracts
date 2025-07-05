"""liquidgold URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store.views import register, spanish, lottery, warnings, create_checkout_session, success, cancel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('store/', include('store.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', register, name='register'),
    path('spanish/', spanish, name='spanish'),
    path('lottery/', lottery, name='lottery'),
    path('warnings/', warnings, name='warnings'),
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
URL configuration for wedding_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# wedding_project/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from wedding_app import views
from wedding_app.api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.guest_login, name='guest_login'),
    path('register/', views.guest_register, name='guest_register'),
    path('upload/', views.guest_upload, name='guest_upload'),
    path('couple/', views.couple_view, name='couple_view'),
    path('api/photo/viewed/<int:photo_id>/', views.mark_photo_viewed, name='mark_photo_viewed'),
    path('api/', api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
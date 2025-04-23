# wedding_site/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from wedding_app import views
from wedding_app.api import api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.upload_photo, name='home'),
    path('register/', views.register_guest, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='guest/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('upload/', views.upload_photo, name='upload_photo'),
    path('gallery/', views.couple_gallery, name='couple_gallery'),
    path('api/', api.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
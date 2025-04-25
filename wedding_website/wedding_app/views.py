# wedding_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .models import WeddingUser, GuestPhoto
from .forms import GuestLoginForm, GuestRegistrationForm, PhotoUploadForm
import os
from django.conf import settings

def guest_login(request):
    if request.method == 'POST':
        form = GuestLoginForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            
            try:
                user = WeddingUser.objects.get(first_name=first_name, last_name=last_name)
                # Pass the backend directly to the login function
                login(request, user, backend='wedding_app.auth_backends.NameBackend')
                
                if user.is_couple:
                    return redirect('couple_view')
                return redirect('guest_upload')
            except WeddingUser.DoesNotExist:
                # If user doesn't exist, redirect to registration
                return redirect('guest_register')
    else:
        form = GuestLoginForm()
    
    return render(request, 'wedding_app/guest_login.html', {'form': form})

def guest_register(request):
    if request.method == 'POST':
        form = GuestRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_couple = False
            user.save()
            # Explicitly specify the backend like we did in guest_login
            login(request, user, backend='wedding_app.auth_backends.NameBackend')
            return redirect('guest_upload')
    else:
        form = GuestRegistrationForm()
    
    return render(request, 'wedding_app/guest_register.html', {'form': form})

@login_required
def guest_upload(request):
    # Check if user is a couple (should not access this page)
    if request.user.is_couple:
        return redirect('couple_view')
    
    # Check if user already uploaded a photo
    try:
        photo = GuestPhoto.objects.get(user=request.user)
        has_uploaded = True
    except GuestPhoto.DoesNotExist:
        photo = None
        has_uploaded = False
    
    if request.method == 'POST':
        if has_uploaded:
            form = PhotoUploadForm(request.POST, request.FILES, instance=photo)
        else:
            form = PhotoUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Check storage limit before saving
            current_storage = get_current_storage_usage()
            max_storage = 200 * 1024 * 1024  # 200MB in bytes
            
            if current_storage >= max_storage:
                messages.error(request, "Storage limit reached. Please contact the website administrator.")
                return redirect('guest_upload')
            
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            
            messages.success(request, "Your photo has been uploaded successfully!")
            return redirect('guest_upload')
    else:
        if has_uploaded:
            form = PhotoUploadForm(instance=photo)
        else:
            form = PhotoUploadForm()
    
    storage_info = get_storage_info()
    return render(request, 'wedding_app/guest_upload.html', {
        'form': form, 
        'has_uploaded': has_uploaded,
        'photo': photo,
        'storage_info': storage_info
    })

@login_required
def couple_view(request):
    # Only allow couple to access this page
    if not request.user.is_couple:
        raise PermissionDenied
    
    photos = GuestPhoto.objects.all().order_by('-upload_date')
    total_photos = photos.count()
    viewed_photos = photos.filter(is_viewed=True).count()
    heart_fill_percentage = (viewed_photos / total_photos * 100) if total_photos > 0 else 0
    
    return render(request, 'wedding_app/couple_view.html', {
        'photos': photos,
        'total_photos': total_photos,
        'viewed_photos': viewed_photos,
        'heart_fill_percentage': heart_fill_percentage
    })

@login_required
def mark_photo_viewed(request, photo_id):
    # Only allow couple to access this
    if not request.user.is_couple:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    try:
        photo = GuestPhoto.objects.get(id=photo_id)
        photo.is_viewed = True
        photo.save()
        
        # Count total photos and viewed photos for heart fill percentage
        total_photos = GuestPhoto.objects.count()
        viewed_photos = GuestPhoto.objects.filter(is_viewed=True).count()
        heart_fill_percentage = (viewed_photos / total_photos) * 100 if total_photos > 0 else 0
        
        return JsonResponse({
            'success': True, 
            'viewed_photos': viewed_photos,
            'total_photos': total_photos,
            'heart_fill_percentage': heart_fill_percentage
        })
    except GuestPhoto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Photo not found'})

def get_current_storage_usage():
    """Calculate current storage usage of uploaded photos"""
    photos_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
    total_size = 0
    
    if os.path.exists(photos_dir):
        for dirpath, dirnames, filenames in os.walk(photos_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
    
    return total_size

def get_storage_info():
    """Get storage information for display"""
    current_usage = get_current_storage_usage()
    max_storage = 200 * 1024 * 1024  # 200MB in bytes
    
    # Convert to MB for display
    current_usage_mb = current_usage / (1024 * 1024)
    max_storage_mb = 200
    
    # Calculate percentage
    percentage = (current_usage / max_storage) * 100 if max_storage > 0 else 0
    
    is_warning = percentage > 80
    
    return {
        'current_usage_mb': round(current_usage_mb, 2),
        'max_storage_mb': max_storage_mb,
        'percentage': round(percentage, 1),
        'is_warning': is_warning
    }
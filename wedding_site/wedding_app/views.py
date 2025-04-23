from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.conf import settings
import os
from .models import Photo, Profile
from .forms import GuestRegistrationForm, PhotoUploadForm

def register_guest(request):
    if request.method == 'POST':
        form = GuestRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for the user
            Profile.objects.create(user=user, is_couple=False)
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
    else:
        form = GuestRegistrationForm()
    
    return render(request, 'guest/register.html', {'form': form})

@login_required
def upload_photo(request):
    # Check if user already uploaded a photo
    try:
        existing_photo = Photo.objects.get(user=request.user)
        has_uploaded = True
    except Photo.DoesNotExist:
        has_uploaded = False
        existing_photo = None
    
    # Check total storage usage
    total_size = get_storage_usage()
    storage_limit = 200 * 1024 * 1024  # 200MB in bytes
    storage_warning = total_size > (storage_limit * 0.85)  # 85% of limit
    
    if request.method == 'POST':
        # Handle existing photo update
        if has_uploaded:
            form = PhotoUploadForm(request.POST, request.FILES, instance=existing_photo)
            success_message = 'Your photo has been updated!'
        else:
            form = PhotoUploadForm(request.POST, request.FILES)
            success_message = 'Your photo has been uploaded!'
        
        if form.is_valid():
            # Check if we're over storage limit
            if total_size > storage_limit:
                messages.error(request, 'Storage limit reached. Please contact the couple.')
                return redirect('upload_photo')
            
            if not has_uploaded:
                photo = form.save(commit=False)
                photo.user = request.user
                photo.save()
            else:
                form.save()
                
            messages.success(request, success_message)
            return redirect('upload_photo')
    else:
        if has_uploaded:
            form = PhotoUploadForm(instance=existing_photo)
        else:
            form = PhotoUploadForm()
    
    context = {
        'form': form,
        'has_uploaded': has_uploaded,
        'storage_warning': storage_warning,
        'existing_photo': existing_photo
    }
    
    return render(request, 'guest/upload.html', context)

@login_required
def couple_gallery(request):
    # Check if user is part of the couple
    try:
        profile = Profile.objects.get(user=request.user)
        if not profile.is_couple:
            messages.error(request, 'You do not have permission to view this page.')
            return redirect('upload_photo')
    except Profile.DoesNotExist:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('upload_photo')
    
    # Get all photos
    photos = Photo.objects.all().order_by('?')  # Random order
    
    # Mark photos as viewed when the couple sees them
    unviewed_photos = photos.filter(is_viewed=False)
    for photo in unviewed_photos:
        photo.is_viewed = True
        photo.save()
    
    context = {
        'photos': photos,
        'viewed_count': Photo.objects.filter(is_viewed=True).count(),
        'total_count': photos.count()
    }
    
    return render(request, 'couple/gallery.html', context)

def get_storage_usage():
    # Calculate total storage usage of uploads
    photos_size = Photo.objects.aggregate(Sum('image'))['image__sum'] or 0
    media_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
    
    # If aggregation doesn't work, manually calculate
    if not photos_size and os.path.exists(media_dir):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(media_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
    
    return photos_size
from django.conf import settings
from ninja import NinjaAPI, Schema
from ninja.security import django_auth
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import Photo
from typing import List, Optional
import os

api = NinjaAPI(auth=django_auth)

class PhotoSchema(Schema):
    id: int
    image: str
    message: Optional[str]
    upload_date: str
    is_viewed: bool
    user_name: str

class StorageSchema(Schema):
    used_bytes: int
    total_bytes: int
    percentage: float
    warning: bool

@api.get("/photos", response=List[PhotoSchema])
def list_photos(request):
    # Ensure user is part of the couple (checking in the view)
    photos = Photo.objects.all()
    result = []
    
    for photo in photos:
        result.append({
            "id": photo.id,
            "image": photo.image.url,
            "message": photo.message,
            "upload_date": photo.upload_date.strftime("%Y-%m-%d %H:%M"),
            "is_viewed": photo.is_viewed,
            "user_name": f"{photo.user.first_name} {photo.user.last_name}"
        })
    
    return result

@api.post("/photos/{photo_id}/view")
def mark_photo_viewed(request, photo_id: int):
    photo = get_object_or_404(Photo, id=photo_id)
    photo.is_viewed = True
    photo.save()
    return {"success": True}

@api.get("/storage", response=StorageSchema)
def get_storage_info(request):
    # Total storage for photos
    total_storage = 200 * 1024 * 1024  # 200MB
    
    # Calculate current usage
    photos_size = Photo.objects.aggregate(Sum('image'))['image__sum'] or 0
    
    # If aggregation doesn't work, calculate manually
    if not photos_size:
        media_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
        if os.path.exists(media_dir):
            total_used = 0
            for dirpath, dirnames, filenames in os.walk(media_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_used += os.path.getsize(fp)
            photos_size = total_used
    
    percentage = (photos_size / total_storage) * 100 if total_storage > 0 else 0
    
    return {
        "used_bytes": photos_size,
        "total_bytes": total_storage,
        "percentage": percentage,
        "warning": percentage > 85  # Warning at 85% usage
    }
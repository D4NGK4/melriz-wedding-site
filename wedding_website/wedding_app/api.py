# wedding_app/api.py
from ninja import NinjaAPI, Schema
from typing import List, Optional
from django.shortcuts import get_object_or_404
from .models import GuestPhoto

api = NinjaAPI()

class PhotoOut(Schema):
    id: int
    image_url: str
    message: Optional[str]
    user_first_name: str
    user_last_name: str
    is_viewed: bool

@api.get("/photos", response=List[PhotoOut])
def get_photos(request):
    # Only allow couple to access this API
    if not request.user.is_couple:
        return []
    
    photos = GuestPhoto.objects.all().order_by('-upload_date')
    
    result = []
    for photo in photos:
        result.append({
            "id": photo.id,
            "image_url": photo.image.url,
            "message": photo.message,
            "user_first_name": photo.user.first_name,
            "user_last_name": photo.user.last_name,
            "is_viewed": photo.is_viewed
        })
    
    return result

@api.post("/photos/{photo_id}/view")
def mark_photo_viewed(request, photo_id: int):
    # Only allow couple to access this API
    if not request.user.is_couple:
        return {"success": False, "error": "Permission denied"}
    
    photo = get_object_or_404(GuestPhoto, id=photo_id)
    photo.is_viewed = True
    photo.save()
    
    # Count total photos and viewed photos for heart fill percentage
    total_photos = GuestPhoto.objects.count()
    viewed_photos = GuestPhoto.objects.filter(is_viewed=True).count()
    heart_fill_percentage = (viewed_photos / total_photos) * 100 if total_photos > 0 else 0
    
    return {
        "success": True,
        "viewed_photos": viewed_photos,
        "total_photos": total_photos,
        "heart_fill_percentage": heart_fill_percentage
    }
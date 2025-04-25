# wedding_app/utils.py
import os
import shutil
from django.conf import settings
from .models import GuestPhoto

def get_storage_info():
    """
    Get detailed storage information
    Returns a dictionary with storage details
    """
    # Calculate storage used by media files
    media_size = get_directory_size(settings.MEDIA_ROOT)
    
    # Calculate storage used by static files
    static_size = get_directory_size(settings.STATIC_ROOT)
    
    # Calculate storage used by the database
    db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    
    # Calculate total storage used
    total_used = media_size + static_size + db_size
    
    # PythonAnywhere free tier limit is 500MB
    storage_limit = 500 * 1024 * 1024  # 500MB in bytes
    available = storage_limit - total_used
    
    # Warning threshold (80% of total)
    warning_threshold = storage_limit * 0.8
    
    return {
        'media_size': media_size,
        'static_size': static_size,
        'db_size': db_size,
        'total_used': total_used,
        'storage_limit': storage_limit,
        'available': available,
        'warning': total_used > warning_threshold,
        'percentage_used': (total_used / storage_limit) * 100
    }

def get_directory_size(directory):
    """
    Calculate the size of a directory and its contents
    """
    total_size = 0
    if os.path.exists(directory):
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
    return total_size

def clean_unused_files():
    """
    Remove any files in the media directory that are not linked to a GuestPhoto
    """
    photos_dir = os.path.join(settings.MEDIA_ROOT, 'photos')
    
    if not os.path.exists(photos_dir):
        return 0
    
    # Get list of all files in the photos directory
    all_files = set()
    for dirpath, dirnames, filenames in os.walk(photos_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            all_files.add(rel_path)
    
    # Get list of all files referenced in the database
    db_files = set()
    for photo in GuestPhoto.objects.all():
        db_files.add(photo.image.name)
    
    # Find files that are not referenced in the database
    unused_files = all_files - db_files
    
    # Delete unused files
    bytes_deleted = 0
    for file_path in unused_files:
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if os.path.exists(full_path):
            bytes_deleted += os.path.getsize(full_path)
            os.remove(full_path)
    
    return bytes_deleted
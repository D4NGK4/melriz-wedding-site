# wedding_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class WeddingUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, is_couple=False):
        user = self.model(
            first_name=first_name,
            last_name=last_name,
            is_couple=is_couple
        )
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, password=None, **extra_fields):
        # Ignore password as we're not using it, but Django will provide it
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            is_couple=True
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class WeddingUser(AbstractBaseUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_couple = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'id'  # We'll use the ID as the unique identifier
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = WeddingUserManager()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        unique_together = ('first_name', 'last_name')
    
    @property
    def is_staff(self):
        return self.is_admin
    
    @property
    def is_superuser(self):
        return self.is_admin
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return self.is_admin

# Replace your compress_image function in models.py with this improved version

def compress_image(uploaded_image):
    """Compress and resize image to save storage space while preserving aspect ratio"""
    img = Image.open(uploaded_image)
    
    # Calculate aspect ratio
    width, height = img.size
    aspect_ratio = width / height
    
    # Set maximum dimensions
    max_width = 1200
    max_height = 1200
    
    # Resize to maximum dimensions while preserving aspect ratio
    if width > max_width or height > max_height:
        if aspect_ratio > 1:  # Landscape orientation
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:  # Portrait orientation
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
        
        # Use high quality resampling
        img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Save image
    output = BytesIO()
    
    # Get file format
    file_format = None
    file_extension = None
    
    # Check file extension from the name
    if uploaded_image.name:
        file_name = uploaded_image.name.lower()
        if file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
            file_format = 'JPEG'
            file_extension = 'jpg'
        elif file_name.endswith('.png'):
            file_format = 'PNG'
            file_extension = 'png'
        elif file_name.endswith('.gif'):
            file_format = 'GIF'
            file_extension = 'gif'
        elif file_name.endswith('.bmp'):
            file_format = 'BMP'
            file_extension = 'bmp'
    
    # Default to JPEG if format is still unknown
    if not file_format:
        file_format = 'JPEG'
        file_extension = 'jpg'
        # Convert to RGB for JPEG format
        if img.mode != 'RGB':
            img = img.convert('RGB')
    
    # Save with better quality
    if file_format == 'JPEG':
        img.save(output, format=file_format, quality=85, optimize=True)
    else:
        # For PNG, don't convert to JPEG to maintain transparency
        img.save(output, format=file_format, optimize=True)
    
    output.seek(0)
    
    # Generate new filename
    if uploaded_image.name:
        filename = os.path.basename(uploaded_image.name)
        name, _ = os.path.splitext(filename)
    else:
        name = 'image'
    
    new_filename = f"{name}.{file_extension}"
    
    return InMemoryUploadedFile(
        output, 'ImageField', new_filename, 
        f'image/{file_extension}', sys.getsizeof(output), None
    )

def photo_upload_path(instance, filename):
    """Define upload path for guest photos"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create new filename with user's name
    new_filename = f"{instance.user.first_name}_{instance.user.last_name}.{ext}"
    return os.path.join('photos', new_filename)

class GuestPhoto(models.Model):
    user = models.OneToOneField(WeddingUser, on_delete=models.CASCADE, related_name='photo')
    image = models.ImageField(upload_to=photo_upload_path)
    message = models.TextField(blank=True, null=True)
    is_viewed = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo from {self.user}"
    
    def save(self, *args, **kwargs):
        # Compress image before saving
        if self.image:
            self.image = compress_image(self.image)
        super().save(*args, **kwargs)
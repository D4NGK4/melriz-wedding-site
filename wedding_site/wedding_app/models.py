from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_couple = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Photo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='photos/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    message = models.TextField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Photo by {self.user.first_name} {self.user.last_name}"
    
    def save(self, *args, **kwargs):
        # Optimize image before saving
        if self.image:
            img = Image.open(self.image)
            
            # Convert to RGB if not already
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to max dimensions while maintaining aspect ratio
            max_size = (1200, 1200)
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Reduce quality for JPEG
            output = BytesIO()
            img.save(output, format='JPEG', quality=75, optimize=True)
            output.seek(0)
            
            # Replace original file with optimized version
            self.image = InMemoryUploadedFile(
                output, 'ImageField', 
                f"{self.image.name.split('.')[0]}.jpg",
                'image/jpeg', sys.getsizeof(output), None
            )
        
        super().save(*args, **kwargs)
# wedding_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import WeddingUser, GuestPhoto

@admin.register(WeddingUser)
class WeddingUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'is_couple', 'is_admin', 'created_at')
    list_filter = ('is_couple', 'is_admin')
    search_fields = ('first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_couple', 'is_admin')}),
    )

@admin.register(GuestPhoto)
class GuestPhotoAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'photo_preview', 'has_message', 'is_viewed', 'upload_date')
    list_filter = ('is_viewed', 'upload_date')
    search_fields = ('user__first_name', 'user__last_name', 'message')
    ordering = ('-upload_date',)
    
    def user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_display.short_description = 'Guest'
    
    def photo_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return "No Image"
    photo_preview.short_description = 'Photo'
    
    def has_message(self, obj):
        return bool(obj.message)
    has_message.boolean = True
    has_message.short_description = 'Has Message'
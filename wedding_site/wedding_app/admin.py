# wedding_app/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Photo

# Define inline admin for Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

# Extend the existing User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_couple')
    
    def get_is_couple(self, obj):
        try:
            return obj.profile.is_couple
        except Profile.DoesNotExist:
            return False
    
    get_is_couple.short_description = 'Is Couple'
    get_is_couple.boolean = True

# Register Photo model
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'upload_date', 'is_viewed')
    list_filter = ('is_viewed', 'upload_date')
    search_fields = ('user__first_name', 'user__last_name', 'message')
    date_hierarchy = 'upload_date'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
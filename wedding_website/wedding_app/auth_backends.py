# wedding_app/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from .models import WeddingUser

class NameBackend(ModelBackend):
    def authenticate(self, request, first_name=None, last_name=None, **kwargs):
        try:
            user = WeddingUser.objects.get(first_name=first_name, last_name=last_name)
            return user
        except WeddingUser.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return WeddingUser.objects.get(pk=user_id)
        except WeddingUser.DoesNotExist:
            return None
# wedding_app/forms.py
from django import forms
from .models import WeddingUser, GuestPhoto

class GuestLoginForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

class GuestRegistrationForm(forms.ModelForm):
    class Meta:
        model = WeddingUser
        fields = ['first_name', 'last_name']
    
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if WeddingUser.objects.filter(first_name=first_name, last_name=last_name).exists():
            raise forms.ValidationError("A guest with this name already exists. Please use a unique name.")
        
        return cleaned_data

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = GuestPhoto
        fields = ['image', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Write a message to the couple (optional)'}),
        }
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Photo

class GuestRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username field hidden and auto-generated from first_name and last_name
        self.fields['username'].widget = forms.HiddenInput()
        self.fields['username'].required = False
        
        # Add old rose styling
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control',
                'style': 'border-color: #c48f97;'
            })
    
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        # Auto-generate username from first and last name
        if first_name and last_name:
            base_username = f"{first_name.lower()}_{last_name.lower()}"
            username = base_username
            counter = 1
            
            # Check if username exists and append numbers until unique
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                
            cleaned_data['username'] = username
        
        return cleaned_data

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'placeholder': 'Write your message for the couple here...',
                'rows': 4,
                'class': 'form-control',
                'style': 'border-color: #c48f97;'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'style': 'border-color: #c48f97;'
            })
        }
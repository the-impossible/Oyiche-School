# My Django import
from django import forms

# My App imports
from oyiche_basic.models import *

class ContactUsForm(forms.ModelForm):

    name = forms.CharField(help_text='Enter your full nname', strip=True, empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text'
        }
    ))

    email = forms.EmailField(help_text='Enter a valid email address', empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'email'
        }
    ))

    phone = forms.CharField(help_text='Enter a valid phone number', strip=True, empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'number'
        }
    ))

    message = message = forms.CharField(
    widget=forms.Textarea(
        attrs={
            'class': 'form-control'
        }
    )
)

    class Meta:
        model = ContactUs
        fields = ('name', 'email', 'phone', 'message')


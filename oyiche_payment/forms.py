# My Django app imports
from django import forms

# My App imports
from oyiche_payment.models import *

class BuyUnitsForm(forms.Form):
    units = forms.CharField(help_text='Enter number of units', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'min':'1',
            'value':'1',
        }
    ))

    amount = forms.CharField(help_text='amount is automatically computed', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'value':'400'
        }
    ))

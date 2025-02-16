# My Django import
from django import forms

# My App imports
from oyiche_auth.models import *

class SchoolForm(forms.ModelForm):

    username = forms.CharField(help_text='Please enter username', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    password = forms.CharField(help_text='Enter Password', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
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


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != None:
            if User.objects.filter(email=email.lower().strip()).exists():
                raise forms.ValidationError('Email Already taken!')

        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone != None:
            if User.objects.filter(phone=phone).exists():
                raise forms.ValidationError('Phone Number Already taken!')

        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            username = generateID(self, self.school)

        if User.objects.filter(username=username.upper().strip()).exists():
            raise forms.ValidationError('Username already exist!')

        return username.upper()

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            password = PASSWORD

        if len(password) < 6:
            raise forms.ValidationError("Password is too short!")

        return password

    def save(self, commit=True):
        user = super().save(commit=False)

        user.set_password(self.cleaned_data.get('password'))

        if commit:
            user.save()

        return user

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password')


class ProfleEditForm(forms.ModelForm):

    email = forms.EmailField(required=False, help_text='Enter a valid email address', empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'email'
        }
    ))

    phone = forms.CharField(required=False, help_text='Enter a valid phone number', strip=True, empty_value=None, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'number'
        }
    ))

    pic = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            check = User.objects.filter(email=email.lower().strip())
            if self.instance:
                check = check.exclude(pk=self.instance.pk)
            if check.exists():
                raise forms.ValidationError('Email Already taken!')

        return email

    def clean_phone(self):

        phone = self.cleaned_data.get('phone')
        if phone:
            check = User.objects.filter(phone=phone)
            if self.instance:
                check = check.exclude(pk=self.instance.pk)
            if check.exists():
                raise forms.ValidationError('Phone Number Already taken!')

        return phone

    class Meta:
        model = User
        fields = ('email', 'phone', 'pic',)

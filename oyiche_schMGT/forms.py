# My Django app imports
from django import forms
# import pandas as pd

# My App imports
from oyiche_schMGT.models import *
from oyiche_auth.models import *
from oyiche_schMGT.utils import *


class GetStudentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(GetStudentForm, self).__init__(*args, **kwargs)

        if self.school:
            self.fields['student_class'].queryset = SchoolClasses.objects.filter(school_info=self.school)
            self.fields['student_class'].label_from_instance = lambda obj: obj.class_name

            self.fields['academic_session'].queryset = AcademicSession.objects.filter(school_info=self.school)

        else:
            self.fields['student_class'].queryset = SchoolClasses.objects.none()

    student_class = forms.ModelChoiceField(queryset=SchoolClasses.objects.none(), empty_label="(Select student class)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    academic_session = forms.ModelChoiceField(queryset=AcademicSession.objects.none(), empty_label="(Select academic session)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    academic_status = forms.ModelChoiceField(queryset=AcademicStatus.objects.all(), empty_label="(Select academic status)", required=False, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

class UploadReportForm(forms.Form):

    student_class = forms.ModelChoiceField(queryset=SchoolClasses.objects.all(), empty_label="(Select student class)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    class_subject = forms.ModelChoiceField(queryset=AcademicSession.objects.all(), empty_label="(Select academic session)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    academic_status = forms.ModelChoiceField(queryset=AcademicStatus.objects.all(), empty_label="(Select academic status)", required=False, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))


class UserForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(UserForm, self).__init__(*args, **kwargs)


    username = forms.CharField(required=False, help_text='Please enter studentID', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    password = forms.CharField(required=False, help_text='Enter Password', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'password',
        }
    ))

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
            raise forms.ValidationError('StudentID already exist!')

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
        fields = ('username', 'email', 'phone', 'pic', 'password')


class StudentInformationForm(forms.ModelForm):
    student_name = forms.CharField(help_text='Please enter student Fullname', strip=True, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))

    gender = forms.ModelChoiceField(queryset=Gender.objects.all(), empty_label="(Select student gender)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    class Meta:
        model = StudentInformation
        fields = ('student_name', 'gender',)


class StudentEnrollmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(StudentEnrollmentForm, self).__init__(*args, **kwargs)

        if self.school:
            self.fields['student_class'].queryset = SchoolClasses.objects.filter(school_info=self.school)
            self.fields['student_class'].label_from_instance = lambda obj: obj.class_name

        else:
            self.fields['student_class'].queryset = SchoolClasses.objects.none()

    student_class = forms.ModelChoiceField(queryset=SchoolClasses.objects.none(), empty_label="(Select student class)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    class Meta:
        model = StudentEnrollment
        fields = ('student_class',)

class EditUserForm(forms.ModelForm):


    username = forms.CharField(required=False, help_text='Please enter studentID', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
        }
    ))


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

    def clean_username(self):

        username = self.cleaned_data.get('username')
        check = User.objects.filter(username=username.upper().strip())

        if self.instance:
            check = check.exclude(pk=self.instance.pk)

        if check.exists():
            raise forms.ValidationError('StudentID already exist!')

        return username.upper()

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'pic',)


class SchoolClassesForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(SchoolClassesForm, self).__init__(*args, **kwargs)


    class_name = forms.CharField(help_text='enter class name', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text',
        }
    ))

    def clean_class_name(self):
        class_name = self.cleaned_data.get('class_name').lower()

        if SchoolClasses.objects.filter(school_info=self.school, class_name=class_name).exists():
            raise forms.ValidationError(f"The class name '{class_name}' already exists for this school.")

        return class_name

    class Meta:
        model = SchoolClasses
        fields = ('class_name',)


class SchoolSubjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(SchoolSubjectForm, self).__init__(*args, **kwargs)


    subject_name = forms.CharField(help_text='enter subject name', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text',
        }
    ))

    def clean_subject_name(self):
        subject_name = self.cleaned_data.get('subject_name').lower()

        if SchoolSubject.objects.filter(school_info=self.school, subject_name=subject_name).exists():
            raise forms.ValidationError(f"The subject '{subject_name}' already exists for this school.")

        return subject_name

    class Meta:
        model = SchoolSubject
        fields = ('subject_name',)



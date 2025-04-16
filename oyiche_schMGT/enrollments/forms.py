# My Django app imports
from django import forms

# My App imports
from oyiche_schMGT.models import *
from oyiche_auth.models import *
from oyiche_schMGT.utils import *

class EnrollmentRequestForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(EnrollmentRequestForm, self).__init__(*args, **kwargs)

        if self.school:
            self.fields['student_class'].queryset = SchoolClasses.objects.filter(school_info=self.school)
            self.fields['student_class'].label_from_instance = lambda obj: obj.class_name.upper()

            self.fields['academic_session'].queryset = AcademicSession.objects.filter(school_info=self.school)
            self.fields['academic_term'].queryset = AcademicTerm.objects.filter(school_info=self.school)

        else:
            self.fields['student_class'].queryset = SchoolClasses.objects.none()
            self.fields['academic_session'].queryset = AcademicSession.objects.none()
            self.fields['academic_term'].queryset = AcademicTerm.objects.none()

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

    academic_term = forms.ModelChoiceField(queryset=AcademicTerm.objects.none(), empty_label="(Select academic term)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    academic_status = forms.ModelChoiceField(queryset=AcademicStatus.objects.all(), empty_label="(Select academic status)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

class EnnrollmentMigrationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(EnnrollmentMigrationForm, self).__init__(*args, **kwargs)

        if self.school:
            self.fields['student_class'].queryset = SchoolClasses.objects.filter(school_info=self.school)
            self.fields['student_class'].label_from_instance = lambda obj: obj.class_name.upper()
            self.fields['academic_status'].queryset = AcademicStatus.objects.filter(status__in=['completed', 'inactive'])

        else:
            self.fields['student_class'].queryset = SchoolClasses.objects.none()
            self.fields['academic_status'].queryset = AcademicStatus.objects.none()

    student_class = forms.ModelChoiceField(queryset=SchoolClasses.objects.none(), empty_label="(Select student class)", help_text="new academic class", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    academic_status = forms.ModelChoiceField(queryset=AcademicStatus.objects.none(), empty_label="(Select academic status)",help_text="mark current enrollment status as?", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))


# My Django app imports
from django import forms
import openpyxl, re
# My App imports
from oyiche_schMGT.models import *
from oyiche_auth.models import *
from oyiche_schMGT.utils import *

class FileHandler:
    def __init__(self, obj):
        self.data = pd.read_excel(obj)
        self.obj = obj

    def validate_file(self):


        # Check if it's actually and excel file
        try:
            wb = openpyxl.load_workbook(self.obj)
        except Exception as e:
            raise forms.ValidationError('Invalid Excel FILE1')

        # Check if the number of columns is 3
        column_length = len(self.data.columns)
        if column_length not in [3,]:
            raise forms.ValidationError('Invalid Excel FILE2')

        # Check for missing values
        missing_data = self.data.isnull().sum()

        if missing_data.any():
            raise forms.ValidationError('Excel File Contains Missing DATA!!')

        # Check for duplicates in the data
        duplicates = self.data[self.data.duplicated(
            subset=[self.data.columns[0]])]

        if not duplicates.empty:
            studentID = duplicates.iloc[0, 0]
            raise forms.ValidationError(
                f'File contains duplicated studentID: {studentID}')


class UploadStudentFeeForm(forms.Form):

    file = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.xlsx'
        }
    ))

    def clean(self):
        cleaned_data = super().clean()

        uploaded_file = cleaned_data.get('file')

        if not uploaded_file:
            raise forms.ValidationError("No file uploaded.")

        if not uploaded_file.name.endswith('.xlsx'):
            raise forms.ValidationError("Invalid Excel File.")

        try:
            handler = FileHandler(obj=uploaded_file)
            handler.validate_file()
        except Exception as e:
            raise forms.ValidationError(f"File validation failed: {str(e)}")

        return cleaned_data


class SchoolFeeEditForm(forms.ModelForm):

    has_paid = forms.BooleanField(required=False, help_text='is the student fees paid?')

    class Meta:
        model = StudentEnrollment
        fields = ('has_paid',)
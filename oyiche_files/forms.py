# My Django app imports
from django import forms
import pandas as pd
import openpyxl

# My App imports
from oyiche_files.models import *
from oyiche_auth.models import *


class FileHandler:
    def __init__(self, obj, file_type):
        self.data = pd.read_excel(obj)
        self.obj = obj
        self.file_type = file_type

    def validate_file(self):

        # Check if it's actually and excel file
        try:
            wb = openpyxl.load_workbook(self.obj)
        except Exception as e:
            raise forms.ValidationError('Invalid Excel FILE')

        # Check if the number of columns is 2 or 3
        column_length = len(self.data.columns)
        if column_length not in [2, 3]:
            raise forms.ValidationError('Invalid Excel FILE')

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

        # Check if record is already created on the database
        if self.file_type in ['Registration']:
            for index, row in self.data.iterrows():
                studentID = row.iloc[0].upper()

                if User.objects.filter(username=studentID).exists():
                    raise forms.ValidationError(
                        f'File contains already registered studentID! {studentID}')

        if str(self.file_type) in ['School Fees']:
            if column_length != 2:
                raise forms.ValidationError(
                    f'Invalid School Fees Data Format!')


class FilesManagerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(FilesManagerForm, self).__init__(*args, **kwargs)

        if self.school:
            self.fields['class_name'].queryset = SchoolClasses.objects.filter(
                school_info=self.school)
            self.fields['class_name'].label_from_instance = lambda obj: obj.class_name
        else:
            self.fields['class_name'].queryset = SchoolClasses.objects.none()

    file = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.xlsx'
        }
    ))

    class_name = forms.ModelChoiceField(queryset=SchoolClasses.objects.none(), empty_label="(Select student class)", required=False, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    file_type = forms.ModelChoiceField(queryset=FileType.objects.all(), empty_label="(Select file type)", required=True,  widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    def clean(self):
        cleaned_data = super().clean()

        uploaded_file = cleaned_data.get('file')
        file_type = cleaned_data.get('file_type')
        class_name = cleaned_data.get('class_name')

        # * class_name * Select a valid choice. That choice is not one of the available choices. * __all__ * File Type 'Registration' requires student class.

        print(f"CLASSNAME: {class_name}")

        if str(file_type) == 'Registration' and not class_name:
            raise forms.ValidationError(
                "File Type 'Registration' requires student class.")

        if not uploaded_file:
            raise forms.ValidationError("No file uploaded.")

        if not uploaded_file.name.endswith('.xlsx'):
            raise forms.ValidationError("Invalid Excel File.")

        try:
            handler = FileHandler(obj=uploaded_file, file_type=file_type)
            handler.validate_file()
        except Exception as e:
            raise forms.ValidationError(f"File validation failed: {str(e)}")

        return cleaned_data

    class Meta:
        model = FilesManager
        fields = ('file', 'class_name', 'file_type')

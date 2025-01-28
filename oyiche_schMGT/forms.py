# My Django app imports
from django import forms
import openpyxl

# My App imports
from oyiche_schMGT.models import *
from oyiche_auth.models import *
from oyiche_schMGT.utils import *

class FileHandler:
    def __init__(self, obj, school, student_class, subject, session, term):
        self.data = pd.read_excel(obj)
        self.obj = obj
        self.school = school
        self.student_class = student_class
        self.subject = subject
        self.session = session
        self.term = term

    def validate_file(self):

        # Check if it's actually and excel file
        try:
            wb = openpyxl.load_workbook(self.obj)
        except Exception as e:
            raise forms.ValidationError('Invalid Excel FILE')

        # Check if the number of columns is 6
        column_length = len(self.data.columns)
        if column_length not in [6,]:
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

        # Check if records are already created in the database
        for index, row in self.data.iterrows():
            # Get student ID and normalize it
            student_id = row.iloc[0].strip().upper()

            try:
                # Validate that these columns are numeric
                ca1 = int(row.iloc[2])  # First CA
                ca2 = int(row.iloc[3])  # Second CA
                ca3 = int(row.iloc[4])  # Third CA
                exam = int(row.iloc[5])  # Exam

                # Check if the values are well in range
                if ca1 < 0 or ca1 > 10:
                    raise forms.ValidationError(
                        f"First CA score must be between 0 and 10 in row {index + 1}"
                    )

                if ca2 < 0 or ca2 > 10:
                    raise forms.ValidationError(
                        f"Second CA score must be between 0 and 10 in row {index + 1}"
                    )

                if ca3 < 0 or ca3 > 10:
                    raise forms.ValidationError(
                        f"Third CA score must be between 0 and 10 in row {index + 1}"
                    )

                if exam < 0 or exam > 70:
                    raise forms.ValidationError(
                        f"Exam score must be between 0 and 70 in row {index + 1}"
                    )

            except (ValueError, TypeError):
                raise forms.ValidationError(
                    f"Invalid numeric value in row {index + 1}. Ensure CA1, CA2, CA3, and Exam are numbers."
                )

            # Fetch the student from the database
            try:
                user = User.objects.get(username=student_id)

                student = StudentInformation.objects.filter(school=self.school, user=user).first()
                school_class_subject = SchoolClassSubjects.objects.filter(school_info=self.school, school_class=self.student_class, school_subject=self.subject).first()

                if not student:
                    raise forms.ValidationError(f"Student with ID [{student_id}] is not registered!")

                # Check if the student's score for the specific subject, session, and term already exists
                if StudentScores.objects.filter(
                    student=student,
                    school_info=self.school,
                    session=self.session,
                    term=self.term,
                    subject=school_class_subject
                ).exists():
                    raise forms.ValidationError(
                        f"Grade for {self.subject} already exists for student ID: {student_id}!"
                    )

                # Check if student was enrolled to the class
                if not StudentEnrollment.objects.filter(student=student, student_class=self.student_class, academic_session=self.session, academic_term=self.term).exists():
                    raise forms.ValidationError(f"Student with ID {student_id} is not enrolled to this class, check file!")

            except User.DoesNotExist:
                raise forms.ValidationError(f"Student with ID {student_id} is not registered!")

class GetStudentForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(GetStudentForm, self).__init__(*args, **kwargs)

        if self.school:
            self.fields['student_class'].queryset = SchoolClasses.objects.filter(school_info=self.school)
            self.fields['student_class'].label_from_instance = lambda obj: obj.class_name.upper()

            self.fields['academic_session'].queryset = AcademicSession.objects.filter(school_info=self.school)
            self.fields['academic_status'].queryset = AcademicStatus.objects.filter(school_info=self.school)

        else:
            self.fields['student_class'].queryset = SchoolClasses.objects.none()
            self.fields['academic_session'].queryset = AcademicSession.objects.none()
            self.fields['academic_status'].queryset = AcademicStatus.objects.none()

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

    academic_status = forms.ModelChoiceField(queryset=AcademicStatus.objects.none(), empty_label="(Select academic status)", required=False, widget=forms.Select(
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
            self.fields['student_class'].label_from_instance = lambda obj: obj.class_name.upper()

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

class SchoolClassSubjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.school = kwargs.pop('school', '')
        self.school_class = kwargs.pop('school_class', '')

        super(SchoolClassSubjectForm, self).__init__(*args, **kwargs)

        if self.school and self.school_class:
            # Get all subjects already assigned to the given school and class
            assigned_subjects = SchoolClassSubjects.objects.filter(
                school_info=self.school,
                school_class=self.school_class
            ).values_list('school_subject', flat=True)

            # Exclude these subjects from the queryset for school_subject
            self.fields['school_subject'].queryset = SchoolSubject.objects.filter(
                school_info=self.school
            ).exclude(id__in=assigned_subjects)

            # Customize the display of the subject names
            self.fields['school_subject'].label_from_instance = lambda obj: obj.subject_name.upper()


    school_subject = forms.ModelChoiceField(queryset=SchoolSubject.objects.none(), empty_label="(Select subject)", required=True, widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    class Meta:
        model = SchoolClassSubjects
        fields = ('school_subject',)

class SchoolGradeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', '')
        super(SchoolGradeForm, self).__init__(*args, **kwargs)

    grade_letter = forms.CharField(help_text='enter grade letter', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text',
        }
    ))

    min_score = forms.CharField(help_text='enter minimum score (inclusive)', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    max_score = forms.CharField(help_text='enter maximum score (inclusive)', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    grade_description = forms.CharField(help_text='enter grade description', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'type': 'text',
        }
    ))

    def clean(self):
        cleaned_data = super().clean()
        min_score = cleaned_data.get('min_score')
        max_score = cleaned_data.get('max_score')

        if min_score is not None and max_score is not None:
            if int(min_score) > int(max_score):
                raise forms.ValidationError("Minimum score grade cannot be greater than Maximum score.")

        return cleaned_data

    def clean_grade_letter(self):
        grade_letter = self.cleaned_data.get('grade_letter').upper()

        if SchoolGrades.objects.filter(school_info=self.school, grade_letter=grade_letter).exists():
            raise forms.ValidationError(f"The Grade '{grade_letter}' already exists.")

        return grade_letter

    def clean_min_score(self):
        min_score = self.cleaned_data.get('min_score')

        if int(min_score) < 0:
            raise forms.ValidationError("Minimum score cannot be less than 0")

        if int(min_score) > 100:
            raise forms.ValidationError("Minimum score cannot be greater than 100")

        return min_score

    def clean_max_score(self):
        max_score = self.cleaned_data.get('max_score')

        if int(max_score) < 0:
            raise forms.ValidationError("Maximum score cannot be less than 0")

        if int(max_score) > 100:
            raise forms.ValidationError("Maximum score cannot be greater than 100")

        return max_score


    class Meta:
        model = SchoolGrades
        fields = ('grade_letter','min_score', 'max_score', 'grade_description',)

class SchoolGradeEditForm(SchoolGradeForm):

    def clean_grade_letter(self):

        grade_letter = self.cleaned_data.get('grade_letter').upper()
        check = SchoolGrades.objects.filter(school_info=self.school, grade_letter=grade_letter)

        if self.instance:
            check = check.exclude(pk=self.instance.pk)

        if check.exists():
            raise forms.ValidationError('Grade Letter already exist!')

        return grade_letter

class UploadStudentSubjectGradeForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.school = kwargs.pop('school', '')
        self.school_class = kwargs.pop('school_class', '')

        self.session = AcademicSession.objects.get(school_info=self.school, is_current=True)
        self.term = AcademicTerm.objects.get(school_info=self.school, is_current=True)

        super(UploadStudentSubjectGradeForm, self).__init__(*args, **kwargs)

        if self.school and self.school_class:

            # Get all subjects already assigned to the given school and class
            assigned_subjects = SchoolClassSubjects.objects.filter(
                school_info=self.school,
                school_class=self.school_class
            ).values_list('school_subject', flat=True)

            # Get subjects that already have scores for the specified session and term
            uploaded_subjects = StudentScores.objects.filter(
                school_info=self.school,
                subject__school_class=self.school_class,
                session=self.session,
                term=self.term
            ).values_list('subject__school_subject', flat=True)

            # Filter subjects that have not been uploaded
            available_subjects = SchoolSubject.objects.filter(
                id__in=assigned_subjects
            ).exclude(id__in=uploaded_subjects)

            # Customize the display of the subject names
            self.fields['subject_name'].queryset = available_subjects
            self.fields['subject_name'].label_from_instance = lambda obj: obj.subject_name.upper()
        else:
            self.fields['subject_name'].queryset = SchoolClassSubjects.objects.none()

    file = forms.FileField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.xlsx'
        }
    ))

    subject_name = forms.ModelChoiceField(queryset=SchoolClassSubjects.objects.none(), empty_label="(Select subject name)", widget=forms.Select(
        attrs={
            'class': 'form-control input-height',
        }
    ))

    def clean(self):
        cleaned_data = super().clean()

        uploaded_file = cleaned_data.get('file')
        subject_name = cleaned_data.get('subject_name')

        if not uploaded_file:
            raise forms.ValidationError("No file uploaded.")

        if not uploaded_file.name.endswith('.xlsx'):
            raise forms.ValidationError("Invalid Excel File.")

        try:
            handler = FileHandler(obj=uploaded_file, school=self.school, student_class=self.school_class, subject=subject_name, session=self.session, term=self.term)
            handler.validate_file()
        except Exception as e:
            raise forms.ValidationError(f"File validation failed: {str(e)}")

        return cleaned_data

class StudentScoreGradeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        self.school = kwargs.pop('school', '')
        self.school_class = kwargs.pop('school_class', '')

        self.session = AcademicSession.objects.get(school_info=self.school, is_current=True)
        self.term = AcademicTerm.objects.get(school_info=self.school, is_current=True)

        super(StudentScoreGradeForm, self).__init__(*args, **kwargs)

        # if self.school and self.student and self.session and self.term:
        if self.school and self.school_class:

            # Get all subjects already assigned to the given school and class
            all_subjects = SchoolClassSubjects.objects.filter(school_info=self.school, school_class=self.school_class)

            # Get all student for the class and school
            all_students = StudentEnrollment.objects.filter(student_class=self.school_class, student__school=self.school).values_list('student', flat=True)

            # Customize the display of the subject names
            self.fields['subject'].queryset = all_subjects
            self.fields['subject'].label_from_instance = lambda obj: obj.school_subject.subject_name.upper()

            self.fields['student'].queryset = StudentInformation.objects.filter(pk__in=all_students)
            self.fields['student'].label_from_instance = lambda obj: f'{obj.user.username.upper()} {obj.student_name.title()}'

    student = forms.ModelChoiceField(queryset=StudentEnrollment.objects.none(), empty_label="(Select student)", widget=forms.Select(
        attrs={
            'class': 'form-control input-height custom_searchable',
            'style': 'width: 100%;',
        }
    ))

    subject = forms.ModelChoiceField(queryset=SchoolClassSubjects.objects.none(), empty_label="(Select subject name)", widget=forms.Select(
        attrs={
            'class': 'form-control input-height custom_searchable',
            'style': 'width: 100%; height: 100px;',
        }
    ))

    first_ca = forms.CharField(help_text='student first CA', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    second_ca = forms.CharField(help_text='student second CA', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    third_ca = forms.CharField(help_text='student third CA', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    exam = forms.CharField(help_text='student exam score', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    def clean_first_ca(self):
        first_ca = int(self.cleaned_data.get('first_ca'))

        if first_ca < 0 or first_ca > 10:
            raise forms.ValidationError("First CA score must be between 0 and 10")

        return first_ca

    def clean_second_ca(self):
        second_ca = int(self.cleaned_data.get('second_ca'))

        if second_ca < 0 or second_ca > 10:
            raise forms.ValidationError("Second CA score must be between 0 and 10")

        return second_ca

    def clean_third_ca(self):
        third_ca = int(self.cleaned_data.get('third_ca'))

        if third_ca < 0 or third_ca > 10:
            raise forms.ValidationError("Third CA score must be between 0 and 10")

        return third_ca

    def clean_exam(self):
        exam = int(self.cleaned_data.get('exam'))

        if exam < 0 or exam > 70:
            raise forms.ValidationError("Exam score must be between 0 and 70")

        return exam

    def clean(self):
        cleaned_data = super().clean()

        student = cleaned_data.get('student')
        subject = cleaned_data.get('subject')

        if StudentScores.objects.filter(
            student=student,
            school_info=self.school,
            session=self.session,
            term=self.term,
            subject=subject
        ).exists():
            raise forms.ValidationError(
                f"Grade for {subject.school_subject.subject_name.upper()} already exists for student ID: {student.user.username}"
            )

        return cleaned_data

    class Meta:
        model = StudentScores
        fields = ('student', 'subject', 'first_ca', 'second_ca', 'third_ca', 'exam',)

class GetStudentSubjectGradeForm(forms.Form):

    def __init__(self, *args, **kwargs):

        self.school = kwargs.pop('school', '')
        self.school_class = kwargs.pop('school_class', '')

        self.session = AcademicSession.objects.get(school_info=self.school, is_current=True)
        self.term = AcademicTerm.objects.get(school_info=self.school, is_current=True)

        super(GetStudentSubjectGradeForm, self).__init__(*args, **kwargs)

        if self.school and self.school_class:

            # Get all subjects already assigned to the given school and class
            assigned_subjects = SchoolClassSubjects.objects.filter(
                school_info=self.school,
                school_class=self.school_class
            )

            # Customize the display of the subject names
            self.fields['subject_name'].queryset = assigned_subjects
            self.fields['subject_name'].label_from_instance = lambda obj: obj.school_subject.subject_name.upper()

        else:
            self.fields['subject_name'].queryset = SchoolClassSubjects.objects.none()


    subject_name = forms.ModelChoiceField(queryset=SchoolClassSubjects.objects.none(), empty_label="(Select subject name)", widget=forms.Select(
        attrs={
            'class': 'form-control input-height custom_searchable',
            'style': 'width: 100%;',
        }
    ))

class StudentScoreGradeEditForm(forms.ModelForm):

    first_ca = forms.CharField(help_text='student first CA', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    second_ca = forms.CharField(help_text='student second CA', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    third_ca = forms.CharField(help_text='student third CA', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    exam = forms.CharField(help_text='student exam score', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'type': 'number',
        }
    ))

    def clean_first_ca(self):
        first_ca = int(self.cleaned_data.get('first_ca'))

        if first_ca < 0 or first_ca > 10:
            raise forms.ValidationError("First CA score must be between 0 and 10")

        return first_ca

    def clean_second_ca(self):
        second_ca = int(self.cleaned_data.get('second_ca'))

        if second_ca < 0 or second_ca > 10:
            raise forms.ValidationError("Second CA score must be between 0 and 10")

        return second_ca

    def clean_third_ca(self):
        third_ca = int(self.cleaned_data.get('third_ca'))

        if third_ca < 0 or third_ca > 10:
            raise forms.ValidationError("Third CA score must be between 0 and 10")

        return third_ca

    def clean_exam(self):
        exam = int(self.cleaned_data.get('exam'))

        if exam < 0 or exam > 70:
            raise forms.ValidationError("Exam score must be between 0 and 70")

        return exam

    class Meta:
        model = StudentScores
        fields = ('first_ca', 'second_ca', 'third_ca', 'exam',)
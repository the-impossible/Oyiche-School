import os
import django
from django.core.files import File

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oyiche_school.settings')
django.setup()

from oyiche_schMGT.models import *
from oyiche_auth.models import *
from oyiche_files.models import *
from oyiche_payment.models import *

# Create Academic Term
academic_term = [
    {
        'term': 'First Term',
        'term_description': 'First term of the academic session'
    },
    {
        'term': 'Second Term',
        'term_description': 'Second term of the academic session'
    },
    {
        'term': 'Third Term',
        'term_description': 'Third term of the academic session'
    },
]

[GeneralAcademicTerm.objects.get_or_create(**term) for term in academic_term]

# Create Academic status
academic_status = [
    {
        'status': 'active',
        'status_description': 'student is currently in the enrolled class'
    },
    {
        'status': 'inactive',
        'status_description': 'student no longer in the system'
    },
    {
        'status': 'completed',
        'status_description': 'student has completed the enrolled class'
    },
]

[AcademicStatus.objects.get_or_create(**status) for status in academic_status]

# Create Gender
student_genders = ['Male', 'Female']
[Gender.objects.get_or_create(gender_title=gender) for gender in student_genders]

# Create UserTypes
user_types = [
    {
        'user_title': 'superuser',
        'user_description': 'This is a superuser role'
    },
    {
        'user_title': 'school',
        'user_description': 'This is a school role'
    },
    {
        'user_title': 'admin',
        'user_description': 'This is an admin role'
    },
    {
        'user_title': 'student',
        'user_description': 'This is a student role'
    },
]

[UserType.objects.get_or_create(**types) for types in user_types]

# Create File Template Types
template_types = ['with studentID', 'without studentID', 'Fees', 'grading']
[FileTemplateType.objects.get_or_create(template_title=types) for types in template_types]

# Create File Types
file_types = ['School Fees', 'Registration']
[FileType.objects.get_or_create(file_title=types) for types in file_types]

# Create School Categories
school_categories = [
    {
        'category_title': 'Private',
        'category_description': 'Private school'
    },
    {
        'category_title': 'Public',
        'category_description': 'Public School'
    },
]

[SchoolCategory.objects.get_or_create(**category) for category in school_categories]

# Create Product Cost
product_cost = [
    {
        'product_cost': 500,
        'company_incentive': 400,
        'school_incentive': 100,
    },
]

[ProductCost.objects.get_or_create(**product) for product in product_cost]

# Create School Types
school_types = [
    {
        'school_title': 'Nursery',
        'school_description': 'A school that provides early childhood education for children before they begin primary school.'
    },
    {
        'school_title': 'Nursery and Primary',
        'school_description': 'A school that offers both nursery (early childhood education) and primary education for children.'
    },
    {
        'school_title': 'Primary',
        'school_description': 'A school that provides foundational education for children, typically from grades 1 to 6.'
    },
    {
        'school_title': 'Primary and Secondary',
        'school_description': 'A school that offers both primary and secondary education, covering early education and advanced levels.'
    },
    {
        'school_title': 'Secondary',
        'school_description': 'A school that provides education after primary school, typically from junior secondary to senior secondary levels.'
    },
    {
        'school_title': 'Nursery, Primary, and Secondary',
        'school_description': 'A school that provides a complete education pathway from nursery, through primary, to secondary level.'
    },
]

[SchoolType.objects.get_or_create(**types) for types in school_types]

# FilesTemplates
file_path = ['assets/student_with_ID_template.xlsx', 'assets/student_without_ID_template.xlsx', 'assets/student_fees_template.xlsx', 'assets/student_report_template.xlsx']

# for index, path in enumerate(file_path):
#     with open(path, 'rb') as file:
#         FilesTemplates.objects.get_or_create(template_type=FileTemplateType.objects.get(template_title=template_types[index]), file=File(file))


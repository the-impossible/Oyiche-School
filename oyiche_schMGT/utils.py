# My django imports
import threading  # for enhancing page functionality
from django.conf import settings  # to gain access to variables from the settings
from django.http import request  # to gain access to the request object
from django.views import View
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages  # for sending messages
import pandas as pd
from django.db import transaction
from django.contrib.auth.hashers import make_password

# My App imports
from oyiche_files.models import FilesManager
from oyiche_auth.models import *
from oyiche_schMGT.models import *

PASSWORD = '12345678'


class BatchAccountCreationThread(threading.Thread):
    def __init__(self, file, school):
        self.file = file
        self.school = school
        threading.Thread.__init__(self)

    def create_batch_account(self):
        df = pd.read_excel(self.file.file)

        # Get number of columns in file
        column_length = len(df.columns)

        # Check if record exist
        duplicate_error = "Duplicate records found in the file, processing halted due to an existing entry for StudentIDs:"
        successful_message = "File has been processed successfully!"
        duplicate_ids = []

        usernames = df.iloc[:, 0].str.upper()
        duplicate_ids = usernames[usernames.isin(
            User.objects.values_list('username', flat=True))]

        if not duplicate_ids.empty:
            duplicate_error += ','.join(duplicate_ids)
            self.file.processing_status = duplicate_error[:200]
        else:
            student_account_list = []

            student_profile_list = []
            student_profile_data = []
            student_enrollment_list = []

            # Query all genders once and store them in a dictionary
            gender_map = {gender.gender_title: gender for gender in Gender.objects.filter(
                gender_title__in=['Male', 'Female'])}

            # Access genders from the dictionary
            male_gender = gender_map.get('Male')
            female_gender = gender_map.get('Female')

            # Get session & term
            session = self.school.school_academic_session.filter(
                is_current=True).first()
            term = self.school.school_academic_term.filter(
                is_current=True).first()
            student_count = StudentEnrollment.objects.filter(
                student__school=self.school, academic_session=session, academic_term=term).count()
            local_counter = student_count

            def generateID(self):

                # Get school username
                school_username = self.school.school_username.upper()

                nonlocal local_counter
                is_taken = True
                student_id = ''

                while is_taken:
                    # Generate the new student ID
                    _counter = local_counter + 1
                    student_id = f"{school_username}{session.session[-2:]}{str(_counter).zfill(4)}"
                    user = User.objects.filter(username=student_id).exists()

                    if not user:
                        is_taken = False

                    local_counter = _counter

                return student_id

            for index, row in df.iterrows():

                if column_length == 3:  # use studentID from file
                    username = row.iloc[0].upper()
                    student_name = row.iloc[1].title()
                    student_gender = female_gender if row.iloc[2].upper(
                    ) == 'F' else male_gender

                else:
                    username = generateID(self)
                    student_name = row.iloc[0].title()
                    student_gender = female_gender if row.iloc[1].upper(
                    ) == 'F' else male_gender

                # Create User -> User
                student_account_list.append(User(username=username, password=make_password(
                    PASSWORD), userType=UserType.objects.get(user_title="student")))

                # Collect profile data for later processing
                student_profile_data.append({
                    'student_id': username,
                    'student_name': student_name,
                    'student_gender': student_gender,
                })

            # Create Student Profile -> StudentInformation

            academic_status = AcademicStatus.objects.get(status="active")

            # Use Atomic transaction
            with transaction.atomic():
                # Create student user account
                created_users = User.objects.bulk_create(student_account_list)

                # Prepare student account profile for bulk creating
                for user, profile_data in zip(created_users, student_profile_data):
                    student_profile_list.append(StudentInformation(
                        student_name=profile_data['student_name'],
                        gender=profile_data['student_gender'],
                        school=self.school,
                        user=user
                    ))

                # Create student account profile
                student_profile_account = StudentInformation.objects.bulk_create(
                    student_profile_list)

                # Prepare student enrollment info for bulk creating
                student_class = self.file.class_name
                for profile in student_profile_account:
                    student_enrollment_list.append(StudentEnrollment(
                        student=profile, academic_status=academic_status, academic_session=session, academic_term=term, student_class=student_class))

                # Create student enrollment info
                student_enrollment_info = StudentEnrollment.objects.bulk_create(
                    student_enrollment_list)
                self.file.processing_status = successful_message

        self.file.save()

    def upload_student_fees(self):
        df = pd.read_excel(self.file.file)

        self.file.used = False
        self.file.save()

    def run(self,):
        if self.file.file_type.file_title == 'Registration':
            self.create_batch_account()

        if self.file.file_type.file_title == 'School Fees':
            self.upload_student_fees()


class AccountCreation(View):

    def create(self, file, school):
        BatchAccountCreationThread(file=file, school=school).start()


Creation = AccountCreation()


def generateID(self, school):

    session = self.school.school_academic_session.filter(
        is_current=True).first()
    term = self.school.school_academic_term.filter(is_current=True).first()
    student_count = StudentEnrollment.objects.filter(
        student__school=school, academic_session=session, academic_term=term).count()

    # Get school username
    school_username = school.school_username.upper()
    # Generate the new student ID

    is_taken = True
    student_id = ''
    counter = student_count + 1

    while is_taken:
        _counter = counter
        student_id = f"{school_username}{session.session[-2:]}{str(_counter).zfill(4)}"

        user = User.objects.filter(username=student_id).exists()

        if not user:
            is_taken = False
        else:
            counter += 1

    return student_id

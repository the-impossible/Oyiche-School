# My Django imports
from django.db import models
from django.conf import settings
import uuid

# My app imports
from oyiche_auth.models import *

# Create your models here.

# SchoolType (Nursery, Primary, Secondary or All)


class SchoolType(models.Model):
    school_title = models.CharField(max_length=20, unique=True)
    school_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.school_title

    class Meta:
        db_table = 'School Type'
        verbose_name_plural = 'School Type'

# SchoolCategory (Public, Private)


class SchoolCategory(models.Model):
    category_title = models.CharField(max_length=20, unique=True)
    category_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.category_title

    class Meta:
        db_table = 'School Category'
        verbose_name_plural = 'School Categories'

# Academic Session (2024/2025)


class AcademicSession(models.Model):
    session = models.CharField(max_length=20, unique=True)
    session_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.session

    class Meta:
        db_table = 'Academic Session'
        verbose_name_plural = 'Academic Session'

# Academic Status (active, completed)


class AcademicStatus(models.Model):
    status = models.CharField(max_length=20, unique=True)
    status_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.status

    class Meta:
        db_table = 'Academic Status'
        verbose_name_plural = 'Academic Status'

# Term (First Term, Second Term)


class AcademicTerm(models.Model):
    term = models.CharField(max_length=20, unique=True)
    term_description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.term

    class Meta:
        db_table = 'Academic Term'
        verbose_name_plural = 'Academic Term'

# Letter (A, B) -> JS1A


class ClassLetter(models.Model):
    class_letter = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.class_letter

    class Meta:
        db_table = 'Class Letter'
        verbose_name_plural = 'Class Letters'

# Term (First Term, Second Term)


class StudentClass(models.Model):
    student_class = models.CharField(max_length=20)
    class_letters = models.ForeignKey(
        to="ClassLetter", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.student_class} {self.class_letters}"

    class Meta:
        db_table = 'Student Class'
        verbose_name_plural = 'Student Classes'
        constraints = [
            models.UniqueConstraint(
                fields=['student_class', 'class_letters'],
                name='unique_student_class_with_letter'
            )
        ]

# Gender (Male, Female)


class Gender(models.Model):
    gender_title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.gender_title

    class Meta:
        db_table = 'Gender'
        verbose_name_plural = 'Gender'


# School Information (School details)


class SchoolInformation(models.Model):
    sch_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    principal_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=500, db_index=True)
    school_username = models.CharField(
        max_length=20, db_index=True, unique=True)
    school_email = models.CharField(
        max_length=100, db_index=True, unique=True, verbose_name="email address", blank=True, null=True)
    school_logo = models.ImageField(
        null=True, blank=True, upload_to="uploads/logos/")
    school_address = models.CharField(max_length=200, db_index=True)
    school_category = models.OneToOneField(
        to="SchoolCategory", on_delete=models.CASCADE)
    school_type = models.OneToOneField(
        to="SchoolType", on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.school_username

    class Meta:
        db_table = 'School Information'
        verbose_name_plural = 'School Information'

# School Admins (School administrators info)


class SchoolAdminInformation(models.Model):
    sch_admin_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.ForeignKey(to=SchoolInformation, on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} is an admin of {self.school}"

    class Meta:
        db_table = 'School Admin Information'
        verbose_name_plural = 'School Admin Information'

# Student Information (pupils & Student)


class StudentInformation(models.Model):
    student_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.ForeignKey(
        to="SchoolInformation", on_delete=models.CASCADE)
    student_name = models.CharField(max_length=500, db_index=True)
    gender = models.ForeignKey(to="Gender", on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.student_name

    class Meta:
        db_table = 'Student Information'
        verbose_name_plural = 'Student Information'

# Enrollment (Student class history and tracking)


class StudentEnrollment(models.Model):
    enrollment_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    student = models.ForeignKey(
        to="StudentInformation", on_delete=models.CASCADE, related_name="student_information")
    student_class = models.ForeignKey(
        to="StudentClass", on_delete=models.CASCADE, related_name="student_enrollment_class")
    promoted_class = models.ForeignKey(
        to="StudentClass", on_delete=models.CASCADE, blank=True, null=True, related_name="promoted_class")
    school_academic_information = models.ForeignKey(
        to="SchoolAcademicInformation", on_delete=models.CASCADE)
    academic_status = models.ForeignKey(
        to="AcademicStatus", on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student}: {self.student_class}"

    class Meta:
        db_table = 'Student Enrollment'
        verbose_name_plural = 'Student Enrollments'


class SchoolAcademicInformation(models.Model):
    academic_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    school = models.ForeignKey(
        to=SchoolInformation, on_delete=models.CASCADE, related_name='academic_infos')
    academic_session = models.ForeignKey(
        to=AcademicSession, on_delete=models.CASCADE, related_name='academic_session')
    academic_term = models.ForeignKey(
        to=AcademicTerm, on_delete=models.CASCADE, related_name='academic_term')
    is_current = models.BooleanField(default=True)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.school.school_username}:{self.academic_session}"

    class Meta:
        db_table = 'School Academic Information'
        verbose_name_plural = 'School Academic Information'

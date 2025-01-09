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
    school_info = models.ForeignKey(
        to='SchoolInformation', on_delete=models.CASCADE, related_name="school_academic_session", blank=True, null=True)
    is_current = models.BooleanField(default=False)

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
    school_info = models.ForeignKey(
        to='SchoolInformation', on_delete=models.CASCADE, related_name="school_academic_term", blank=True, null=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.term

    class Meta:
        db_table = 'Academic Term'
        verbose_name_plural = 'Academic Term'

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
    school_category = models.ForeignKey(
        to="SchoolCategory", on_delete=models.CASCADE)
    school_type = models.ForeignKey(
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
        to="SchoolClasses", on_delete=models.CASCADE, related_name="student_enrollment_class")
    promoted_class = models.ForeignKey(
        to="SchoolClasses", on_delete=models.CASCADE, blank=True, null=True, related_name="promoted_class")
    academic_session = models.ForeignKey(
        to="AcademicSession", on_delete=models.CASCADE, related_name='student_academic_session', blank=True, null=True)
    academic_term = models.ForeignKey(
        to="AcademicTerm", on_delete=models.CASCADE, related_name='student_academic_term', blank=True, null=True)
    academic_status = models.ForeignKey(
        to="AcademicStatus", on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student}: {self.student_class}"

    class Meta:
        db_table = 'Student Enrollment'
        verbose_name_plural = 'Student Enrollments'


# School Classes (JS1, JS2)
class SchoolClasses(models.Model):
    class_name = models.CharField(max_length=20)
    school_info = models.ForeignKey(
        to=SchoolInformation, on_delete=models.CASCADE, related_name="school_class")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school_info.school_username} {self.class_name}"

    def save(self, *args, **kwargs):
        # Normalize class_name to lowercase for case-insensitivity
        self.class_name = self.class_name.lower()
        super(SchoolClasses, self).save(*args, **kwargs)

    class Meta:
        db_table = 'School Classes'
        verbose_name_plural = 'School Classes'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "class_name"],
                name="unique_class_per_school",
            )
        ]

# School Subjects (English, Mathematics)


class SchoolSubject(models.Model):
    subject_name = models.CharField(max_length=20)
    school_info = models.ForeignKey(
        to=SchoolInformation, on_delete=models.CASCADE, related_name="school_subject")
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school_info.school_username} {self.subject_name}"

    def save(self, *args, **kwargs):
        # Normalize subject_name to lowercase for case-insensitivity
        self.subject_name = self.subject_name.lower()
        super(SchoolSubject, self).save(*args, **kwargs)

    class Meta:
        db_table = 'School Subject'
        verbose_name_plural = 'School Subject'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "subject_name"],
                name="unique_subject_per_school",
            )
        ]


# School Class Subjects (SF:-> English, SF:-> Mathematics)


class SchoolClassSubjects(models.Model):

    school_class = models.ForeignKey(
        to='SchoolClasses', on_delete=models.CASCADE, related_name='school_class')
    school_info = models.ForeignKey(
        to=SchoolInformation, on_delete=models.CASCADE, related_name="school_class_subject", blank=True, null=True)
    school_subject = models.ForeignKey(
        to='SchoolSubject', on_delete=models.CASCADE, related_name='school_subject')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.school_info.username} {self.school_class} {self.school_subject}'

    class Meta:
        db_table = 'School Class Subjects'
        verbose_name_plural = 'School Class Subjects'


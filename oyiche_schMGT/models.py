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
        return f'{self.school_class.class_name} {self.school_subject.subject_name}'

    class Meta:
        db_table = 'School Class Subjects'
        verbose_name_plural = 'School Class Subjects'

# School Grades


class SchoolGrades(models.Model):
    grade_letter = models.CharField(max_length=1)
    min_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=100)
    grade_description = models.CharField(max_length=500, blank=True, null=True)
    school_info = models.ForeignKey(to='SchoolInformation', on_delete=models.CASCADE, related_name='school_grades')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.school_info.school_username} {self.grade_letter}'

    def save(self, *args, **kwargs):
        self.grade_letter = self.grade_letter.upper()
        self.grade_description = self.grade_description.capitalize()

        super(SchoolGrades, self).save(*args, **kwargs)

    class Meta:
        db_table = 'School Grades'
        verbose_name_plural = 'School Grades'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "grade_letter"],
                name="unique_grade_letter_per_school",
            )
        ]

# Student Scores


class StudentScores(models.Model):

    student = models.ForeignKey(
        to='StudentInformation', on_delete=models.CASCADE, related_name='student_scores', blank=True, null=True)
    school_info = models.ForeignKey(
        to='SchoolInformation', on_delete=models.CASCADE, related_name='school_student_scores', blank=True, null=True)
    subject = models.ForeignKey(to='SchoolClassSubjects', on_delete=models.CASCADE, blank=True, null=True, related_name='student_subject_scores')
    term = models.ForeignKey(to='AcademicTerm', on_delete=models.CASCADE, blank=True, null=True, related_name='student_term_scores')
    session = models.ForeignKey(to='AcademicSession', on_delete=models.CASCADE, blank=True, null=True, related_name='student_session_scores')
    grade = models.ForeignKey(to='SchoolGrades', on_delete=models.CASCADE, blank=True, null=True, related_name='student_grade_scores')

    first_ca = models.IntegerField(default=0)
    second_ca = models.IntegerField(default=0)
    third_ca = models.IntegerField(default=0)
    exam = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.school_info.school_username} {self.student.student_name} {self.subject.school_subject.subject_name.upper()}'

    def calculate_grade_and_total_score(self):
        # Calculate total_score
        self.total_score = self.first_ca + self.second_ca + self.third_ca + self.exam

        # Assign grade
        self.grade = SchoolGrades.objects.filter(
            school_info=self.school_info,
            min_score__lte=self.total_score,
            max_score__gte=self.total_score
        ).first()

    class Meta:
        db_table = 'Student Scores'
        verbose_name_plural = 'Student Scores'

# Student Performance


class StudentPerformance(models.Model):

    student = models.ForeignKey(
        to='StudentInformation', on_delete=models.CASCADE, related_name='student_performance', blank=True, null=True)
    school_info = models.ForeignKey(
        to='SchoolInformation', on_delete=models.CASCADE, related_name='school_student_performance', blank=True, null=True)
    current_enrollment = models.ForeignKey(to='StudentEnrollment', on_delete=models.CASCADE, blank=True, null=True, related_name='student_enrollment')

    average_score = models.IntegerField(default=0)
    term_position = models.IntegerField(default=0)
    remark = models.CharField(max_length=500, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} | {self.average_score} | {self.term_position}'

    class Meta:
        db_table = 'Student Performance'
        verbose_name_plural = 'Student Performance'


# My Django imports
from django.db import models
from django.db.models import Min, Max, F, Window
from django.db.models.functions import Rank
from django.conf import settings
import uuid

# My app imports
from oyiche_auth.models import *

# Create your models here.

# SchoolType (Nursery, Primary, Secondary or All)


class SchoolType(models.Model):
    sch_type_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    school_title = models.CharField(max_length=100, unique=True)
    school_description = models.CharField(
        max_length=200, blank=True, null=True)

    def __str__(self):
        return self.school_title

    class Meta:
        verbose_name_plural = 'School Type'

# SchoolCategory (Public, Private)


class SchoolCategory(models.Model):
    sch_category_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    category_title = models.CharField(max_length=20, unique=True)
    category_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.category_title

    class Meta:
        verbose_name_plural = 'School Categories'

# Academic Session (2024/2025)


class AcademicSession(models.Model):
    academic_session_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    session = models.CharField(max_length=20)
    session_description = models.CharField(
        max_length=100, blank=True, null=True)
    school_info = models.ForeignKey(
        to='SchoolInformation', on_delete=models.CASCADE, related_name="school_academic_session", blank=True, null=True)
    is_current = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session

    class Meta:
        verbose_name_plural = 'Academic Session'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "session"],
                name="unique_session_per_school",
            )
        ]

# Academic Status (active, completed)


class AcademicStatus(models.Model):
    academic_status_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    status = models.CharField(max_length=20)
    status_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.status

    class Meta:
        verbose_name_plural = 'Academic Status'

# Term (First Term, Second Term)

class GeneralAcademicTerm(models.Model):
    general_academic_term_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    term = models.CharField(max_length=20)
    term_description = models.CharField(max_length=100, blank=True, null=True)
    is_current = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.term

    class Meta:
        verbose_name_plural = 'General Academic Term'

class AcademicTerm(models.Model):
    academic_term_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    term = models.CharField(max_length=20)
    term_description = models.CharField(max_length=100, blank=True, null=True)
    school_info = models.ForeignKey(
        to='SchoolInformation', on_delete=models.CASCADE, related_name="school_academic_term", blank=True, null=True)
    is_current = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.term

    class Meta:
        verbose_name_plural = 'Academic Term'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "term"],
                name="unique_term_per_school",
            )
        ]


# Gender (Male, Female)


class Gender(models.Model):
    gender_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    gender_title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.gender_title

    class Meta:
        verbose_name_plural = 'Gender'


# School Information (School details)


class SchoolInformation(models.Model):
    sch_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    principal_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=500, db_index=True, blank=True, null=True)
    school_username = models.CharField(
        max_length=20, db_index=True, unique=True, blank=True, null=True)
    school_email = models.CharField(
        max_length=100, db_index=True, unique=True, verbose_name="email address", blank=True, null=True)
    school_logo = models.ImageField(default='img/user.png',
        null=True, blank=True, upload_to="uploads/logos/")
    school_address = models.CharField(max_length=200, db_index=True, blank=True, null=True)
    school_updated = models.BooleanField(default=False, blank=True, null=True)

    school_category = models.ForeignKey(
        to="SchoolCategory", on_delete=models.CASCADE,null=True, blank=True)

    school_type = models.ForeignKey(
        to="SchoolType", on_delete=models.CASCADE,null=True, blank=True)

    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        if self.school_username:
            return self.school_username
        else:
            return f'{self.principal_id.username}'

    class Meta:
        verbose_name_plural = 'School Information'

# School Admins (School administrators info)


class SchoolAdminInformation(models.Model):
    sch_admin_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.ForeignKey(to=SchoolInformation, on_delete=models.CASCADE)
    admin_name = models.CharField(max_length=500, db_index=True, blank=True, null=True)

    gender = models.ForeignKey(to="Gender", on_delete=models.CASCADE, null=True, blank=True)

    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} is an admin of {self.school}"

    class Meta:
        verbose_name_plural = 'School Admin Information'

# Student Information (pupils & Student)


class StudentInformation(models.Model):
    student_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_user")
    school = models.ForeignKey(
        to="SchoolInformation", on_delete=models.CASCADE, related_name='student_school')
    student_name = models.CharField(max_length=500, db_index=True)

    gender = models.ForeignKey(to="Gender", on_delete=models.CASCADE, null=True, blank=True)

    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.student_name

    class Meta:
        verbose_name_plural = 'Student Information'

# Enrollment (Student class history and tracking)


class StudentEnrollment(models.Model):
    enrollment_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    student = models.ForeignKey(
        to="StudentInformation", on_delete=models.CASCADE, related_name="student_information")

    student_class = models.ForeignKey(
        to="SchoolClasses", on_delete=models.CASCADE, related_name="student_enrollment_class", null=True, blank=True)

    promoted_class = models.ForeignKey(
        to="SchoolClasses", on_delete=models.CASCADE, blank=True, null=True, related_name="promoted_class")

    academic_session = models.ForeignKey(
        to="AcademicSession", on_delete=models.CASCADE, related_name='s_academic_session', blank=True, null=True)

    academic_term = models.ForeignKey(
        to="AcademicTerm", on_delete=models.CASCADE, related_name='student_academic_term', blank=True, null=True)

    academic_status = models.ForeignKey(
        to="AcademicStatus", on_delete=models.CASCADE, null=True, blank=True)

    has_paid = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student}: {self.student_class}"

    class Meta:
        verbose_name_plural = 'Student Enrollments'


# School Classes (JS1, JS2)
class SchoolClasses(models.Model):
    class_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
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
        verbose_name_plural = 'School Classes'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "class_name"],
                name="unique_class_per_school",
            )
        ]

# School Subjects (English, Mathematics)


class SchoolSubject(models.Model):
    sch_subject_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
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
        verbose_name_plural = 'School Subject'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "subject_name"],
                name="unique_subject_per_school",
            )
        ]


# School Class Subjects (SF:-> English, SF:-> Mathematics)


class SchoolClassSubjects(models.Model):
    sch_class_subject_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    school_class = models.ForeignKey(
        to='SchoolClasses', on_delete=models.CASCADE, related_name='school_class', null=True, blank=True)

    school_info = models.ForeignKey(
        to=SchoolInformation, on_delete=models.CASCADE, related_name="school_class_subject", blank=True, null=True)

    school_subject = models.ForeignKey(
        to='SchoolSubject', on_delete=models.CASCADE, related_name='school_subject', null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.school_class.class_name} {self.school_subject.subject_name}'

    class Meta:
        verbose_name_plural = 'School Class Subjects'

# School Grades


class SchoolGrades(models.Model):
    sch_grade_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
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
        verbose_name_plural = 'School Grades'
        constraints = [
            models.UniqueConstraint(
                fields=["school_info", "grade_letter"],
                name="unique_grade_letter_per_school",
            )
        ]

# Student Scores


class StudentScores(models.Model):
    student_score_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
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
    average = models.FloatField(default=0)
    total_score = models.IntegerField(default=0)
    position = models.CharField(max_length=10, blank=True, null=True)

    highest_score = models.IntegerField(default=0)
    lowest_score = models.IntegerField(default=0)

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

    def calculate_average(self):
        term =  self.term

        try:

            # Get First Term, Second Term and Third Term in one query
            terms = AcademicTerm.objects.filter(school_info=self.school_info).values('term', 'pk')
            term_dict = {term['term']: term['pk'] for term in terms}

            if len(term_dict) != 3:
                raise ValueError("One or More Academic Term is missing!")

            scores = StudentScores.objects.filter(
                student=self.student,
                session=self.session,
                subject=self.subject,
                term__in=term_dict.values()
            ).values('term', 'total_score')

            score_dict = {score['term']: score['total_score'] for score in scores}

            # Handle missing term scores
            first_term_total_score = score_dict.get(term_dict['First Term'], None)
            second_term_total_score = score_dict.get(term_dict['Second Term'], None)
            third_term_total_score = score_dict.get(term_dict['Third Term'], None)

            # Compute the average based on available scores
            if term.term == 'First Term':
                self.average = self.total_score  # Only First Term exists

            elif term.term == 'Second Term':
                if first_term_total_score is not None:
                    self.average = (first_term_total_score + self.total_score) / 2
                else:
                    self.average = self.total_score  # No First Term record, use Second Term alone

            elif term.term == 'Third Term':
                if first_term_total_score is not None and second_term_total_score is not None:
                    self.average = (first_term_total_score + second_term_total_score + self.total_score) / 3
                elif second_term_total_score is not None:
                    self.average = (second_term_total_score + self.total_score) / 2
                else:
                    self.average = self.total_score  # No prior records, use Third Term alone

        except AcademicTerm.DoesNotExist:

            raise ValueError("Academic Term does not exist!")

    def calculate_highest_and_lowest_score(self):

        # Calculate lowest_score and highest_score in only on query
        score_aggregate = StudentScores.objects.filter(
            session=self.session,
            school_info=self.school_info,
            term=self.term,
            subject=self.subject
        ).aggregate(
            highest_score = Max('total_score'),
            lowest_score = Min('total_score')
        )

        # Extract the lowest_score and highest_score
        highest_score = score_aggregate.get('highest_score') or 0
        lowest_score = score_aggregate.get('lowest_score') or 0

        # Update all related student scores with the highest and lowest scores
        StudentScores.objects.filter(
            session=self.session,
            school_info=self.school_info,
            term=self.term,
            subject=self.subject
        ).update(highest_score=highest_score, lowest_score=lowest_score)

    def calculate_positions(self):
        """
            Calculate positions for all student scores based on average.
        """
        # Retrieve all filtered records
        scores = StudentScores.objects.filter(
            session=self.session,
            term=self.term,
            subject=self.subject,
            school_info=self.school_info
        )

        # Annotate records with their rank based on 'average'
        ranked_scores = scores.annotate(
            rank=Window(
                expression=Rank(),
                order_by=F('average').desc()  # Descending order of average
            )
        )

        # Prepare bulk updates with formatted position
        updates = []
        for score in ranked_scores:
            # Generate position with ordinal suffix
            rank = score.rank
            score.position = f"{rank}{self.get_position_suffix(rank)}"
            updates.append(score)

        # Bulk update positions
        StudentScores.objects.bulk_update(updates, ['position'])

    def get_position_suffix(self, rank):
        """
            Helper function to get the correct ordinal suffix for a rank (e.g., 1st, 2nd, 3rd).
        """
        if 10 <= rank % 100 <= 20:  # Special case for teens (11th, 12th, 13th, etc.)
            return "th"
        else:
            suffix_map = {1: "st", 2: "nd", 3: "rd"}
            return suffix_map.get(rank % 10, "th")

    class Meta:
        verbose_name_plural = 'Student Scores'

# Student Performance

class StudentPerformance(models.Model):
    performance_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    student = models.ForeignKey(
        to='StudentInformation', on_delete=models.CASCADE, related_name='student_performance', blank=True, null=True)
    school_info = models.ForeignKey(
        to='SchoolInformation', on_delete=models.CASCADE, related_name='school_student_performance', blank=True, null=True)
    current_enrollment = models.ForeignKey(to='StudentEnrollment', on_delete=models.CASCADE, blank=True, null=True, related_name='student_enrollment')

    total_marks_obtained = models.IntegerField(default=0)
    total_subject = models.IntegerField(default=0)

    student_average = models.FloatField(default=0)
    class_average = models.FloatField(default=0)

    school_remark = models.ForeignKey(to='SchoolRemark', on_delete=models.CASCADE, blank=True, null=True, related_name='student_performance_remark')

    term_position = models.CharField(max_length=20, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} | {self.student_average} | {self.class_average} | {self.term_position}'

    def calculate_student_average_total_marks_total_subject(self):

        """
            Calculate the average score, total marks, and total subject for a student in the given term, class and session.
        """

        # Get all scores for the student in the current term and session
        current_scores = StudentScores.objects.filter(
            student=self.student,
            school_info=self.school_info,
            term=self.current_enrollment.academic_term,
            session=self.current_enrollment.academic_session
        )
        # Calculate total scores
        total_scores = sum(score.total_score for score in current_scores)

        # Get the total number of subjects for the class
        num_scores = SchoolClassSubjects.objects.filter(
            school_info=self.school_info,
            school_class=self.current_enrollment.student_class
        ).count()

        #  Set the calculated values
        self.student_average = round(total_scores / num_scores, 2) if num_scores > 0 else 0
        self.total_subject = num_scores
        self.total_marks_obtained = total_scores

    def calculate_class_average(self):
        """
            Calculate the class average for the student's class.
            (Sum of all student averages for the class) / (Total Student in the class).
        """

        # Ensure the student's current enrollment and class are defined
        if not self.current_enrollment:
            raise ValueError("Student enrollment not found!")

        # Filter all StudentPerformance records for the same school, class, session, and term
        class_performances = StudentPerformance.objects.filter(
            school_info=self.school_info,
            current_enrollment__student_class=self.current_enrollment.student_class,
            current_enrollment__academic_term=self.current_enrollment.academic_term,
            current_enrollment__academic_session=self.current_enrollment.academic_session,
        )

        # Calculate the total of all student averages for the class
        total_class_averages = sum(performance.student_average for performance in class_performances)

        # Check to prevent division by zero
        if self.student_average == 0:
            raise ValueError("Cannot calculate class average as some student score average is zero, upload those student grades!")

        # Calculate the class average
        self.class_average = round(total_class_averages / class_performances.count(), 2)

    def calculate_term_position(self):
        """
            The ranking is done based on the student's average in descending order.
        """
        # Ensure the student's current enrollment and class are defined
        if not self.current_enrollment:
            raise ValueError(f"{self.student} has no enrollment!")

        # Annotate performances with rank based on descending student averages
        class_performances = StudentPerformance.objects.filter(
            school_info=self.school_info,
            current_enrollment__student_class=self.current_enrollment.student_class,
            current_enrollment__academic_term=self.current_enrollment.academic_term,
            current_enrollment__academic_session=self.current_enrollment.academic_session
        )

        ranked_scores = class_performances.annotate(
            rank=Window(
                expression=Rank(),
                order_by=F('student_average').desc()  # Descending order of average
            )
        )

        # Prepare bulk updates with formatted position
        updates = []
        for score in ranked_scores:
            # Generate position with ordinal suffix
            rank = score.rank
            score.term_position = f"{rank}{self.get_position_suffix(rank)}"
            updates.append(score)

        # Bulk update positions
        StudentPerformance.objects.bulk_update(updates, ['term_position'])

    def get_position_suffix(self, rank):
        """
            Helper function to get the correct ordinal suffix for a rank (e.g., 1st, 2nd, 3rd).
        """
        if 10 <= rank % 100 <= 20:  # Special case for teens (11th, 12th, 13th, etc.)
            return "th"
        else:
            suffix_map = {1: "st", 2: "nd", 3: "rd"}
            return suffix_map.get(rank % 10, "th")

    def calculate_school_remark(self):

        # Assign school remark
        self.school_remark = SchoolRemark.objects.filter(
            school_info=self.school_info,
            min_average__lte=self.student_average,
            max_average__gte=self.student_average
        ).first()

    def save(self, *args, **kwargs):
        self.calculate_student_average_total_marks_total_subject()
        super(StudentPerformance, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Student Performance'

class SchoolRemark(models.Model):
    sch_remark_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    min_average = models.FloatField(default=0)
    max_average = models.FloatField(default=100)
    teacher_remark = models.CharField(max_length=500, blank=True, null=True)
    principal_remark = models.CharField(max_length=500, blank=True, null=True)
    school_info = models.ForeignKey(to='SchoolInformation', on_delete=models.CASCADE, related_name='school_teacher_remark')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.school_info.school_username} {self.teacher_remark}'

    def save(self, *args, **kwargs):
        self.teacher_remark = self.teacher_remark.upper()
        self.principal_remark = self.principal_remark.upper()

        super(SchoolRemark, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'School Remarks'

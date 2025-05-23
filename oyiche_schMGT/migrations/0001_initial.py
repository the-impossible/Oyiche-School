# Generated by Django 5.1.5 on 2025-03-09 17:29

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=20)),
                ('status_description', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name_plural': 'Academic Status',
                'db_table': 'Academic Status',
            },
        ),
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender_title', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Gender',
                'db_table': 'Gender',
            },
        ),
        migrations.CreateModel(
            name='SchoolCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_title', models.CharField(max_length=20, unique=True)),
                ('category_description', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name_plural': 'School Categories',
                'db_table': 'School Category',
            },
        ),
        migrations.CreateModel(
            name='SchoolType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_title', models.CharField(max_length=100, unique=True)),
                ('school_description', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'School Type',
                'db_table': 'School Type',
            },
        ),
        migrations.CreateModel(
            name='SchoolInformation',
            fields=[
                ('sch_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('school_name', models.CharField(blank=True, db_index=True, max_length=500, null=True)),
                ('school_username', models.CharField(blank=True, db_index=True, max_length=20, null=True, unique=True)),
                ('school_email', models.CharField(blank=True, db_index=True, max_length=100, null=True, unique=True, verbose_name='email address')),
                ('school_logo', models.ImageField(blank=True, default='img/user.png', null=True, upload_to='uploads/logos/')),
                ('school_address', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('school_updated', models.BooleanField(blank=True, default=False, null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('principal_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('school_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oyiche_schMGT.schoolcategory')),
                ('school_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oyiche_schMGT.schooltype')),
            ],
            options={
                'verbose_name_plural': 'School Information',
                'db_table': 'School Information',
            },
        ),
        migrations.CreateModel(
            name='SchoolGrades',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_letter', models.CharField(max_length=1)),
                ('min_score', models.IntegerField(default=0)),
                ('max_score', models.IntegerField(default=100)),
                ('grade_description', models.CharField(blank=True, max_length=500, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('school_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_grades', to='oyiche_schMGT.schoolinformation')),
            ],
            options={
                'verbose_name_plural': 'School Grades',
                'db_table': 'School Grades',
            },
        ),
        migrations.CreateModel(
            name='SchoolClasses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.CharField(max_length=20)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('school_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_class', to='oyiche_schMGT.schoolinformation')),
            ],
            options={
                'verbose_name_plural': 'School Classes',
                'db_table': 'School Classes',
            },
        ),
        migrations.CreateModel(
            name='SchoolAdminInformation',
            fields=[
                ('sch_admin_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('admin_name', models.CharField(blank=True, db_index=True, max_length=500, null=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('gender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oyiche_schMGT.gender')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oyiche_schMGT.schoolinformation')),
            ],
            options={
                'verbose_name_plural': 'School Admin Information',
                'db_table': 'School Admin Information',
            },
        ),
        migrations.CreateModel(
            name='AcademicTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(max_length=20)),
                ('term_description', models.CharField(blank=True, max_length=100, null=True)),
                ('is_current', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('school_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_academic_term', to='oyiche_schMGT.schoolinformation')),
            ],
            options={
                'verbose_name_plural': 'Academic Term',
                'db_table': 'Academic Term',
            },
        ),
        migrations.CreateModel(
            name='AcademicSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=20)),
                ('session_description', models.CharField(blank=True, max_length=100, null=True)),
                ('is_current', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('school_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_academic_session', to='oyiche_schMGT.schoolinformation')),
            ],
            options={
                'verbose_name_plural': 'Academic Session',
                'db_table': 'Academic Session',
            },
        ),
        migrations.CreateModel(
            name='SchoolRemark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_average', models.FloatField(default=0)),
                ('max_average', models.FloatField(default=100)),
                ('teacher_remark', models.CharField(blank=True, max_length=500, null=True)),
                ('principal_remark', models.CharField(blank=True, max_length=500, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('school_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_teacher_remark', to='oyiche_schMGT.schoolinformation')),
            ],
            options={
                'verbose_name_plural': 'School Remarks',
                'db_table': 'School Remark',
            },
        ),
        migrations.CreateModel(
            name='SchoolSubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(max_length=20)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('school_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_subject', to='oyiche_schMGT.schoolinformation')),
            ],
            options={
                'verbose_name_plural': 'School Subject',
                'db_table': 'School Subject',
            },
        ),
        migrations.CreateModel(
            name='SchoolClassSubjects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_class', to='oyiche_schMGT.schoolclasses')),
                ('school_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_class_subject', to='oyiche_schMGT.schoolinformation')),
                ('school_subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_subject', to='oyiche_schMGT.schoolsubject')),
            ],
            options={
                'verbose_name_plural': 'School Class Subjects',
                'db_table': 'School Class Subjects',
            },
        ),
        migrations.CreateModel(
            name='StudentInformation',
            fields=[
                ('student_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('student_name', models.CharField(db_index=True, max_length=500)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oyiche_schMGT.gender')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_school', to='oyiche_schMGT.schoolinformation')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Student Information',
                'db_table': 'Student Information',
            },
        ),
        migrations.CreateModel(
            name='StudentEnrollment',
            fields=[
                ('enrollment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('academic_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_academic_session', to='oyiche_schMGT.academicsession')),
                ('academic_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oyiche_schMGT.academicstatus')),
                ('academic_term', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_academic_term', to='oyiche_schMGT.academicterm')),
                ('promoted_class', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='promoted_class', to='oyiche_schMGT.schoolclasses')),
                ('student_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_enrollment_class', to='oyiche_schMGT.schoolclasses')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_information', to='oyiche_schMGT.studentinformation')),
            ],
            options={
                'verbose_name_plural': 'Student Enrollments',
                'db_table': 'Student Enrollment',
            },
        ),
        migrations.CreateModel(
            name='StudentPerformance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_marks_obtained', models.IntegerField(default=0)),
                ('total_subject', models.IntegerField(default=0)),
                ('student_average', models.FloatField(default=0)),
                ('class_average', models.FloatField(default=0)),
                ('term_position', models.CharField(blank=True, max_length=20, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('current_enrollment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_enrollment', to='oyiche_schMGT.studentenrollment')),
                ('school_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_student_performance', to='oyiche_schMGT.schoolinformation')),
                ('school_remark', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_performance_remark', to='oyiche_schMGT.schoolremark')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_performance', to='oyiche_schMGT.studentinformation')),
            ],
            options={
                'verbose_name_plural': 'Student Performance',
                'db_table': 'Student Performance',
            },
        ),
        migrations.CreateModel(
            name='StudentScores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_ca', models.IntegerField(default=0)),
                ('second_ca', models.IntegerField(default=0)),
                ('third_ca', models.IntegerField(default=0)),
                ('exam', models.IntegerField(default=0)),
                ('average', models.FloatField(default=0)),
                ('total_score', models.IntegerField(default=0)),
                ('position', models.CharField(blank=True, max_length=10, null=True)),
                ('highest_score', models.IntegerField(default=0)),
                ('lowest_score', models.IntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('grade', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_grade_scores', to='oyiche_schMGT.schoolgrades')),
                ('school_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_student_scores', to='oyiche_schMGT.schoolinformation')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_session_scores', to='oyiche_schMGT.academicsession')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_scores', to='oyiche_schMGT.studentinformation')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_subject_scores', to='oyiche_schMGT.schoolclasssubjects')),
                ('term', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_term_scores', to='oyiche_schMGT.academicterm')),
            ],
            options={
                'verbose_name_plural': 'Student Scores',
                'db_table': 'Student Scores',
            },
        ),
        migrations.AddConstraint(
            model_name='schoolgrades',
            constraint=models.UniqueConstraint(fields=('school_info', 'grade_letter'), name='unique_grade_letter_per_school'),
        ),
        migrations.AddConstraint(
            model_name='schoolclasses',
            constraint=models.UniqueConstraint(fields=('school_info', 'class_name'), name='unique_class_per_school'),
        ),
        migrations.AddConstraint(
            model_name='academicterm',
            constraint=models.UniqueConstraint(fields=('school_info', 'term'), name='unique_term_per_school'),
        ),
        migrations.AddConstraint(
            model_name='academicsession',
            constraint=models.UniqueConstraint(fields=('school_info', 'session'), name='unique_session_per_school'),
        ),
        migrations.AddConstraint(
            model_name='schoolsubject',
            constraint=models.UniqueConstraint(fields=('school_info', 'subject_name'), name='unique_subject_per_school'),
        ),
    ]

# Generated by Django 5.1.4 on 2025-01-13 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyiche_schMGT', '0010_schoolgrades_studentperformance_studentscores'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolgrades',
            name='grade_letter',
            field=models.CharField(max_length=1),
        ),
        migrations.AddConstraint(
            model_name='schoolgrades',
            constraint=models.UniqueConstraint(fields=('school_info', 'grade_letter'), name='unique_grade_letter_per_school'),
        ),
    ]

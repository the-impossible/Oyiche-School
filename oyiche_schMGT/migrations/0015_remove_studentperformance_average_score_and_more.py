# Generated by Django 5.1.4 on 2025-01-21 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyiche_schMGT', '0014_remove_studentenrollment_school_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentperformance',
            name='average_score',
        ),
        migrations.RemoveField(
            model_name='studentperformance',
            name='remark',
        ),
        migrations.AddField(
            model_name='studentperformance',
            name='class_average',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='studentperformance',
            name='student_average',
            field=models.FloatField(default=0),
        ),
    ]

# Generated by Django 5.1.5 on 2025-02-15 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyiche_schMGT', '0027_remove_academicstatus_unique_status_per_school_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schooltype',
            name='school_description',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

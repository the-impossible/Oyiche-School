# Generated by Django 5.1.5 on 2025-02-06 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyiche_schMGT', '0024_academicsession_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolinformation',
            name='school_logo',
            field=models.ImageField(blank=True, default='img/user.png', null=True, upload_to='uploads/logos/'),
        ),
    ]

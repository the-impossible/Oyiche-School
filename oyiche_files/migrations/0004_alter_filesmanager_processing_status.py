# Generated by Django 5.1.5 on 2025-01-28 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyiche_files', '0003_alter_filesmanager_processing_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesmanager',
            name='processing_status',
            field=models.CharField(default='File has not been processed Yet!', max_length=200),
        ),
    ]

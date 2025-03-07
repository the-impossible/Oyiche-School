# Generated by Django 5.1.5 on 2025-03-05 16:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oyiche_schMGT', '0032_studentperformance_school_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='schooladmininformation',
            name='admin_name',
            field=models.CharField(blank=True, db_index=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='schooladmininformation',
            name='gender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oyiche_schMGT.gender'),
        ),
    ]

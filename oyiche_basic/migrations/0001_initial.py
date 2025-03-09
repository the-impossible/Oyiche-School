# Generated by Django 5.1.5 on 2025-03-09 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(blank=True, db_index=True, max_length=100, null=True, verbose_name='email address')),
                ('phone', models.CharField(blank=True, db_index=True, max_length=11, null=True)),
                ('message', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Contact Us',
                'db_table': 'Contact Us',
            },
        ),
    ]

# My Django imports
from django.db import models
import uuid

# My App imports
from oyiche_schMGT.models import *

# Create your models here.

# File Type (Registration, Fees)


class FileType(models.Model):


    file_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)

    file_title = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.file_title

    class Meta:
        verbose_name_plural = 'File Types'

# File Template Type (with:studentID, without:studentID, Fees)


class FileTemplateType(models.Model):


    file_template_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)

    template_title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.template_title

    class Meta:
        verbose_name_plural = 'File Template Type'


def path_and_rename(instance, filename):
    path = 'uploads/xslx/'
    ext = filename.split('.')[-1]

    filename = f'{instance.class_name.class_name}_{instance.file_type}.{ext}' if instance.class_name else f'{instance.file_type}.{ext}'
    return f'{path}{filename}'


class FilesManager(models.Model):
    file_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    file = models.FileField(upload_to=path_and_rename)

    # class_name = models.ForeignKey(
    #     to=SchoolClasses, on_delete=models.CASCADE, blank=True, null=True)
    class_name = models.ForeignKey(
        to=SchoolClasses, on_delete=models.CASCADE, blank=True, null=True)

    # file_type = models.ForeignKey(to=FileType, on_delete=models.CASCADE)
    file_type = models.ForeignKey(to=FileType, on_delete=models.CASCADE, null=True, blank=True)

    school = models.ForeignKey(to=SchoolInformation, on_delete=models.CASCADE)
    processing_status = models.CharField(
        default="File has not been processed Yet!", max_length=200)
    used = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.file}'

    def delete(self, using=None, keep_parents=False):
        self.file.storage.delete(self.file.name)
        super().delete()

    class Meta:
        verbose_name_plural = 'Files Manager'


class FilesTemplates(models.Model):


    file_template_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)

    file = models.FileField(upload_to='uploads/templates')

    # template_type = models.ForeignKey(
    #     to=FileTemplateType, on_delete=models.CASCADE)
    template_type = models.ForeignKey(
        to=FileTemplateType, on_delete=models.CASCADE, null=True, blank=True)

    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.file}'

    def delete(self, using=None, keep_parents=False):
        self.file.storage.delete(self.file.name)
        super().delete()

    class Meta:
        verbose_name_plural = 'Files Templates'

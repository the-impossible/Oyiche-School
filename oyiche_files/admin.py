# # My Django imports
# from django.contrib import admin


# # My App imports
# from oyiche_files.models import *

# # Register your models here.

# @admin.register(FilesManager)
# class FilesManagerAdmin(admin.ModelAdmin):
#     list_display = ['file_id', 'file', 'used', 'class_name', 'file_type', 'school', 'processing_status', 'date_created']
#     list_editable = ['used', 'class_name', 'file_type', 'processing_status']
#     list_select_related = ['class_name', 'file_type', 'school']
#     list_per_page = 100
#     list_filter = ['used', 'file_type', 'date_created']

# @admin.register(FilesTemplates)
# class FilesTemplatesAdmin(admin.ModelAdmin):
#     list_display = ['file_template_id', 'file', 'template_type', 'date_created']
#     list_filter = ['date_created', ]
#     list_per_page = 100

# @admin.register(FileType)
# class FileTypeAdmin(admin.ModelAdmin):
#     list_display = ['file_type_id', 'file_title']
#     list_editable = ['file_title']
#     list_per_page = 100

# @admin.register(FileTemplateType)
# class FileTemplateTypeAdmin(admin.ModelAdmin):
#     list_display = ['file_template_type_id', 'template_title']
#     list_editable = ['template_title']
#     list_per_page = 100
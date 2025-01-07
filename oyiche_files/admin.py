# My Django imports
from django.contrib import admin


# My App imports
from oyiche_files.models import *

# Register your models here.
class FilesManagerAdmin(admin.ModelAdmin):
    list_display = ('file_id','file', 'used', 'class_name', 'file_type', 'date_created')
    search_fields = ('file', 'used', 'class_name', 'file_type', 'date_created')
    ordering = ('date_created',)
    readonly_fields = ('date_created',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(FilesManager, FilesManagerAdmin)
admin.site.register(FileType)
admin.site.register(FileTemplateType)
admin.site.register(FilesTemplates)
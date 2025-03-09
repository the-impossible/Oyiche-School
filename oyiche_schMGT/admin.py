# My Django app import
from django.contrib import admin

# My app import
from oyiche_schMGT.models import *

# Register your models here.


class SchoolInformationAdmin(admin.ModelAdmin):
    list_display = ('principal_id', 'school_name', 'school_username',
                    'school_email', 'school_category', 'school_type', 'date_created',)
    search_fields = ('school_name', 'school_username',
                     'school_email', 'school_category', 'school_type', 'principal_id__username')
    ordering = ('date_created',)
    readonly_fields = ('date_created',)
    raw_id_fields = ['principal_id',]

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Gender)
admin.site.register(StudentInformation)
admin.site.register(SchoolClasses)
admin.site.register(SchoolInformation, SchoolInformationAdmin)
admin.site.register(SchoolAdminInformation)
admin.site.register(SchoolCategory)
admin.site.register(SchoolType)
admin.site.register(AcademicSession)
admin.site.register(AcademicStatus)
admin.site.register(AcademicTerm)
admin.site.register(StudentEnrollment)
admin.site.register(SchoolGrades)
admin.site.register(StudentScores)
admin.site.register(StudentPerformance)
admin.site.register(SchoolClassSubjects)
admin.site.register(SchoolRemark)


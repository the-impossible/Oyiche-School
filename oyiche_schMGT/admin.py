# # My Django app import
# from django.contrib import admin

# # My app import
# from oyiche_schMGT.models import *

# # Register your models here.
# @admin.register(SchoolInformation)
# class SchoolInformationAdmin(admin.ModelAdmin):
#     autocomplete_fields = ['principal_id', 'school_category', 'school_type']
#     list_display = ['principal_id', 'school_name', 'school_username', 'school_email', 'school_address', 'school_type', 'school_category', 'result_type', 'date_created']
#     list_editable = ['school_email', 'school_address', 'school_type', 'school_category', 'school_username']
#     list_filter = ['date_created', 'school_category', 'school_type']
#     list_per_page = 100
#     list_select_related = ['principal_id', 'school_category', 'school_type']

#     search_fields = ['school_name', 'school_username', 'school_email', 'school_address', 'principal_id']

# @admin.register(Gender)
# class GenderAdmin(admin.ModelAdmin):
#     list_display = ['gender_id', 'gender_title']
#     list_editable = ['gender_title']
#     list_display_links = ['gender_id']
#     search_fields = ['gender_title']

# @admin.register(StudentInformation)
# class StudentInformationAdmin(admin.ModelAdmin):
#     autocomplete_fields = ['user_id', 'school', 'gender']
#     list_display = ['user__username', 'student_name', 'school', 'gender', 'date_created']
#     list_editable = ['student_name']
#     list_select_related = ['user', 'school', 'gender']
#     list_filter = ['school', 'date_created']
#     list_per_page = 100

#     search_fields = ['user__username', 'student_name', 'school__school_username',]

# @admin.register(StudentEnrollment)
# class StudentEnrollmentAdmin(admin.ModelAdmin):
#     autocomplete_fields = ['student', 'academic_session', 'academic_term', 'academic_status',]
#     list_display = ['student', 'student_class', 'academic_session', 'academic_term', 'academic_status', 'has_paid', 'date_created']
#     list_editable = []
#     list_select_related = ['student', 'student_class', 'promoted_class', 'academic_session', 'academic_term', 'academic_status']
#     list_filter = ['has_paid', 'academic_session', 'academic_term', 'academic_status']
#     list_per_page = 100

#     search_fields = ['student__user__username', 'student_class__class_name']

# @admin.register(SchoolAdminInformation)
# class SchoolAdminInformationAdmin(admin.ModelAdmin):

#     list_display = ['user__username', 'school', 'admin_name', 'gender', 'date_created']
#     list_editable = ['admin_name']
#     list_select_related = ['user', 'school', 'gender']
#     list_filter = ['date_created', 'gender']
#     search_fields = ['user__username', 'admin_name', 'school__school_username']

# @admin.register(SchoolClasses)
# class SchoolClassesAdmin(admin.ModelAdmin):
#     list_display = ['class_id', 'class_name', 'school_info', 'date_created']
#     list_editable = ['class_name']
#     list_display_links = ['class_id']
#     list_select_related = ['school_info']
#     list_filter = ['date_created']
#     search_fields = ['class_name', 'school_info__school_username']
#     list_per_page = 100
# @admin.register(SchoolCategory)
# class SchoolCategoryAdmin(admin.ModelAdmin):
#     list_display = ['sch_category_id', 'category_title', 'category_description']
#     list_display_links = ['sch_category_id']
#     list_editable = ['category_description', 'category_title']

#     search_fields = ['category_title']

# @admin.register(SchoolType)
# class SchoolTypeAdmin(admin.ModelAdmin):
#     list_display = ['sch_type_id', 'school_title', 'school_description']
#     list_display_links = ['sch_type_id']
#     list_editable = ['school_description', 'school_title']

#     search_fields = ['school_title']

# @admin.register(AcademicSession)
# class AcademicSessionAdmin(admin.ModelAdmin):
#     list_display = ['academic_session_id', 'session', 'session_description', 'school_info', 'is_current', 'is_completed', 'date_created']
#     list_display_links = ['academic_session_id']
#     list_editable = ['session', 'session_description', 'school_info', 'is_current', 'is_completed']
#     list_select_related = ['school_info']
#     readonly_fields = ['date_created']
#     list_filter = ['is_current', 'is_completed', 'school_info', 'date_created']

#     search_fields = ['session']
#     ordering = ['-date_created']

# @admin.register(AcademicStatus)
# class AcademicStatusAdmin(admin.ModelAdmin):
#     list_display = ['academic_status_id', 'status', 'status_description']
#     list_display_links = ['academic_status_id']
#     list_editable = ['status', 'status_description']
#     list_per_page = 100

#     search_fields = ['status']

# @admin.register(GeneralAcademicTerm)
# class GeneralAcademicTermAdmin(admin.ModelAdmin):
#     list_display = ['general_academic_term_id', 'term', 'term_description', 'is_current', 'date_created']
#     list_display_links = ['general_academic_term_id']
#     list_editable = ['term', 'term_description', 'is_current']
#     list_per_page = 100

#     search_fields = ['term']
#     readonly_fields = ['date_created']

# @admin.register(AcademicTerm)
# class AcademicTermAdmin(admin.ModelAdmin):
#     list_display = ['academic_term_id', 'term', 'term_description', 'school_info', 'is_current', 'date_created']
#     list_display_links = ['academic_term_id']
#     list_editable = ['term', 'term_description', 'school_info', 'is_current']
#     list_select_related = ['school_info', ]
#     readonly_fields = ['date_created']

#     search_fields = ['term']
#     ordering = ['-date_created']

# @admin.register(SchoolGrades)
# class SchoolGradesAdmin(admin.ModelAdmin):
#     list_display = ['sch_grade_id','grade_letter', 'min_score', 'max_score', 'grade_description', 'school_info', 'date_created']
#     list_display_links = ['sch_grade_id']
#     list_editable = ['grade_letter', 'min_score', 'max_score', 'grade_description']
#     list_per_page = 100
#     list_select_related = ['school_info']
#     readonly_fields = ['date_created']
#     search_fields = ['grade_letter', 'grade_description']

# @admin.register(StudentScores)
# class StudentScoresAdmin(admin.ModelAdmin):
#     list_display = ['student_score_id', 'student', 'school_info', 'first_ca', 'second_ca', 'third_ca', 'exam', 'average', 'total_score', 'position', 'session', 'term', 'subject', 'highest_score', 'lowest_score', 'date_created']
#     list_editable = ['first_ca', 'second_ca', 'third_ca', 'exam',]
#     list_select_related = ['student', 'school_info', 'session', 'term', 'subject', 'grade']
#     list_filter = ['session', 'term']
#     list_per_page = 100

#     search_fields = ['student__user__username', 'subject__subject_name']
#     readonly_fields = ['date_created']

# @admin.register(StudentPerformance)
# class StudentPerformanceAdmin(admin.ModelAdmin):
#     list_display = ['performance_id', 'student', 'school_info', 'current_enrollment__student_class', 'total_marks_obtained', 'total_subject', 'student_average', 'class_average', 'term_position', 'date_created']
#     list_editable = []
#     list_select_related = ['student', 'school_info', 'current_enrollment']
#     list_filter = ['current_enrollment__academic_term', 'current_enrollment__academic_session']
#     list_per_page = 100

#     search_fields = ['student__user__username']
#     readonly_fields = ['date_created']

# @admin.register(SchoolClassSubjects)
# class SchoolClassSubjectsAdmin(admin.ModelAdmin):
#     list_display = ['sch_class_subject_id', 'school_info', 'school_class', 'school_subject', 'date_created']
#     list_editable = ['school_class', 'school_subject']
#     list_filter = ['school_info', 'school_class']
#     list_select_related = ['school_info', 'school_class', 'school_subject']
#     list_per_page = 100

#     search_fields = ['school_info__school_username',]
#     readonly_fields = ['date_created']

# @admin.register(SchoolRemark)
# class SchoolRemarkAdmin(admin.ModelAdmin):
#     list_display = ['sch_remark_id', 'school_info', 'min_average', 'max_average', 'teacher_remark', 'principal_remark', 'date_created']
#     list_editable = ['min_average', 'max_average', 'teacher_remark', 'principal_remark']
#     list_select_related = ['school_info']
#     list_per_page = 100

#     search_fields = ['school_info__school_username']
#     readonly_fields = ['date_created']

# # admin.site.register(ResultType)
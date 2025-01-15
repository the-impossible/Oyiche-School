from django.urls import path
from oyiche_schMGT.views import *

app_name = "sch"

urlpatterns = [
    # Students
    path("batch_create/<str:file_id>",
         BatchCreateView.as_view(), name="batch_create"),
    path("students", StudentPageView.as_view(), name="students"),
    path("edit_student/<str:user_id>",
         EditStudentPageView.as_view(), name="edit_student"),

    # Files
    path("file_manager", SchoolFileUploadView.as_view(), name="file_manager"),
    path("delete_file/<str:file_id>",
         DeleteFileView.as_view(), name="delete_file"),

    # Upload Report
    path("upload_report", UploadReportView.as_view(), name="upload_report"),

     # School Classes
     path("school_classes", SchoolClassesView.as_view(), name="school_classes"),
     path("school_subject", SchoolSubjectView.as_view(), name="school_subject"),
     path("subject_class/<str:class_id>", SubjectClassView.as_view(), name="subject_class"),

     # School Grades
     path("school_grade", SchoolGradesView.as_view(), name="school_grade"),
     path("list_school_grades", ListGradesView.as_view(), name="list_school_grades"),
     path("grade_edit_form/<str:grade_id>", GradesEditView.as_view(), name="grade_edit_form"),
     path("grade_delete/<str:grade_id>", GradesDeleteView.as_view(), name="grade_delete"),

     # School Options
     path("school_options/<str:class_id>", SchoolClassOptions.as_view(), name="school_options"),
     path("upload_student_subject_grades/<str:class_id>", UploadStudentSubjectGrades.as_view(), name="upload_student_subject_grades"),

]

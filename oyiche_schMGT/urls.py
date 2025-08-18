from django.urls import path, re_path
from oyiche_schMGT.views import *
from oyiche_schMGT.templates.grades_template import *
from oyiche_schMGT.enrollments.manage_enrollment import *
from oyiche_schMGT.students.students import *
from oyiche_schMGT.fees.student_fees import *

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
     re_path(r'^manage_student_grades/(?P<class_id>[\w-]+)/(?P<subject_id>[\w-]+)?$',
            ManageStudentSubjectGrades.as_view(), name="manage_student_grades"),
     path("score_edit_form/<str:score_id>", StudentScoreEditView.as_view(), name="score_edit_form"),
     path("score_delete/<str:pk>", StudentScoreDeleteView.as_view(), name="score_delete"),

     # Compute Results
     path("compute_results/<str:class_id>", ComputeResultView.as_view(), name="compute_results"),
     path("student_result", StudentResultView.as_view(), name="student_result"),
     path("result_preview/<str:performance_id>", ResultPreviewPage.as_view(), name="result_preview"),
     path("download_multiple_result/<str:class_id>", DownloadMultipleResultPage.as_view(), name="download_multiple_result"),

     # School Details
     path("manage_school_details", ManageSchoolDetailsView.as_view(), name="manage_school_details"),
     path("manage_school_remarks", ManageSchoolResultView.as_view(), name="manage_school_remarks"),

     # Download Templates
     path("export_grade_template/<str:class_id>", ExportGradeTemplateView.as_view(), name="export_grade_template"),
     path("export_fees_template/<str:class_id>", ExportFeeTemplateView.as_view(), name="export_fees_template"),

     # Manage Student Enrollment
     path("enrollments", ManageStudentEnrollment.as_view(), name="enrollments"),

     # Manage Student Fees
     path("manage_student_fees/<str:class_id>", ManageStudentFees.as_view(), name="manage_student_fees"),
     path("fee_edit_form/<str:enrollment_id>", StudentFeeEditView.as_view(), name="fee_edit_form"),
     path("list_school_fees/<str:class_id>", ListStudentFeesView.as_view(), name="list_school_fees"),

]

from django.urls import path
from oyiche_schMGT.views import *

app_name = "sch"

urlpatterns = [
     #Students
    path("batch_create/<str:file_id>",
         BatchCreateView.as_view(), name="batch_create"),
    path("students", StudentPageView.as_view(), name="students"),
    path("edit_student/<str:user_id>", EditStudentPageView.as_view(), name="edit_student"),

     # Files
    path("file_manager", SchoolFileUploadView.as_view(), name="file_manager"),
    path("delete_file/<str:file_id>",
         DeleteFileView.as_view(), name="delete_file"),
]

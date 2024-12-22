from django.urls import path
from oyiche_schMGT.views import *

app_name = "sch"

urlpatterns = [
    path("students", StudentPageView.as_view(), name="students"),
    path("file_manager", SchoolFileUploadView.as_view(), name="file_manager"),
    path("batch_create/<str:file_id>",
         BatchCreateView.as_view(), name="batch_create"),
    path("delete_file/<str:file_id>",
         DeleteFileView.as_view(), name="delete_file"),
]   

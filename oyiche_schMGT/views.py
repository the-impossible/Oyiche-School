# My Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
import pandas as pd

# My App imports
from oyiche_schMGT.models import *
from oyiche_schMGT.forms import *
from oyiche_files.forms import *
from oyiche_files.models import *
from oyiche_schMGT.utils import *
# Create your views here.
def get_school(request):
    school = None

    try:
        school = SchoolAdminInformation.objects.get(user=request.user)
        return school

    except SchoolAdminInformation.DoesNotExist:

        try:
            school = SchoolInformation.objects.get(
                principal_id=request.user)
        except SchoolInformation.DoesNotExist:
            messages.error(
                request, "Profile doesn't exist!!, therefore files list can't be displayed")
            return None
    finally:
        return school

class StudentPageView(LoginRequiredMixin, View):
    template_name = "backend/student/students.html"

    def get(self, request):
        return render(request=request, template_name=self.template_name)




class SchoolFileUploadView(LoginRequiredMixin, ListView):
    template_name = "backend/school/file_manager.html"

    def get_queryset(self):
        school = get_school(self.request)
        if school:
            return FilesManager.objects.filter(school=school).order_by('-date_created')
        return FilesManager.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SchoolFileUploadView, self).get_context_data(**kwargs)
        form = FilesManagerForm()

        # Files Templates for download
        context['with_studentID'] = get_object_or_404(
            FilesTemplates, template_type=FileTemplateType.objects.get(template_title="with studentID"))
        context['without_studentID'] = get_object_or_404(
            FilesTemplates, template_type=FileTemplateType.objects.get(template_title="without studentID"))
        context['fees_template'] = get_object_or_404(
            FilesTemplates, template_type=FileTemplateType.objects.get(template_title="Fees"))
        # Page Form
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        form = FilesManagerForm(data=self.request.POST,
                                files=self.request.FILES)
        self.object_list = self.get_queryset()

        if form.is_valid():
            data = form.save(commit=False)

            school = get_school(self.request)
            if school:
                data.school = school
                data.save()
                messages.success(request, "File uploaded successfully")
            else:
                messages.error(request, "School profile not found!!")

        else:
            messages.error(request, form.errors.as_text())

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class BatchCreateView(LoginRequiredMixin, View):
    def post(self, request, file_id):
        try:
            uploaded_file = FilesManager.objects.get(pk=file_id)

            if not uploaded_file.used:
                Creation.create(uploaded_file, get_school(self.request))

                uploaded_file.processing_status = "Processing File!"
                uploaded_file.used = True
                uploaded_file.save()
                messages.success(self.request, "File is been processed check details!!")

            else:
                messages.error(self.request, "File has been Used Already!!")

        except FilesManager.DoesNotExist:
            messages.error(self.request, "File Not Found!!")
        finally:
            return redirect('sch:file_manager')

class DeleteFileView(LoginRequiredMixin, View):
    def post(self, request, file_id):
        try:
            uploaded_file = FilesManager.objects.get(pk=file_id)
            uploaded_file.delete()
            messages.success(self.request, "File has been Deleted!!")
        except FilesManager.DoesNotExist:
            messages.error(self.request, "File Not Found!!")
        finally:
            return redirect('sch:file_manager')


# My Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
import pandas as pd
from urllib.parse import urlencode
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError

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

    form = GetStudentForm
    user_form = UserForm
    info_form = StudentInformationForm
    enrollment_form = StudentEnrollmentForm
    school = None

    # Context variables
    object_list = None
    all_student = ''
    add_student = ''

    def get(self, request):
        self.school = get_school(request)

        self.all_student = 'active'
        self.add_student = ''

        # Extract filtering parameters
        student_class = request.GET.get("student_class")
        academic_session = request.GET.get("academic_session")
        academic_status = request.GET.get("academic_status")

        query = {}

        # Prepare initial values for the form
        initial_data = {}

        # Filter students if parameters exist
        if student_class and student_class != 'None':
            query["student_class"] = student_class
            initial_data['student_class'] = student_class

        if academic_session and academic_session != 'None':
            query["academic_session"] = academic_session,
            initial_data['academic_session'] = academic_session

        if academic_status and academic_status != 'None':
            query["academic_status"] = academic_status
            initial_data['academic_status'] = academic_status

        if query:
            self.object_list = StudentEnrollment.objects.filter(**query)
            self.form = self.form(initial=initial_data, school=self.school)
        else:
            self.form = self.form(school=self.school)


        return render(request=request, template_name=self.template_name, context={'form': self.form, 'user_form': self.user_form, 'info_form': self.info_form, 'enrollment_form': self.enrollment_form(school=self.school), 'object_list': self.object_list, 'all_student': self.all_student, 'add_student': self.add_student})

    def post(self, request):

        self.school = get_school(request)

        form = self.form(data=request.POST, school=self.school)

        def get_students(self, add_student, all_student):

            nonlocal form
            academic_status = None

            try:
                student_class = form.cleaned_data.get('student_class')
                academic_session = form.cleaned_data.get('academic_session')
                academic_status = form.cleaned_data.get('academic_status')

            except AttributeError:

                student_class = SchoolClasses.objects.get(
                    pk=request.POST.get('student_class'))
                academic_session = AcademicSession.objects.get(
                    pk=request.POST.get('academic_session'))
                status = request.POST.get('academic_status')
                if status:
                    academic_status = AcademicStatus.objects.get(
                        pk=request.POST.get('academic_status'))

            query = {
                'student_class': student_class,
                'academic_session': academic_session,
            }

            if academic_status is not None:
                query['academic_status'] = academic_status

            student_in_class_and_in_session = StudentEnrollment.objects.filter(
                **query)

            self.object_list = student_in_class_and_in_session
            self.form = form

            self.all_student = all_student
            self.add_student = add_student

        if 'get_students' in request.POST:

            if form.is_valid():
                get_students(self, '', 'active')
            else:
                messages.error(request=request, message=form.errors.as_text())

        elif 'delete' in request.POST:
            student_id = request.POST.get('user_id')

            try:
                User.objects.get(user_id=student_id).delete()
                messages.success(
                    request, "Account has been deleted successfully!!")
            except User.DoesNotExist:
                message.error(request, "Failed to delete account!!")
            finally:
                get_students(self, '', 'active')

        elif 'create' in request.POST:
            user_form = self.user_form(
                data=request.POST, files=request.FILES, school=self.school)
            info_form = self.info_form(data=request.POST)
            enrollment_form = self.enrollment_form(data=request.POST, school=self.school)

            # Get session, status & term
            academic_status = AcademicStatus.objects.get(status="active")
            session = self.school.school_academic_session.filter(is_current=True).first()
            term = self.school.school_academic_term.filter(is_current=True).first()

            if user_form.is_valid() and info_form.is_valid() and enrollment_form.is_valid():

                user_form_data = user_form.save(commit=False)
                info_form_data = info_form.save(commit=False)
                enrollment_form_data = enrollment_form.save(commit=False)

                user_form_data.userType = UserType.objects.get(
                    user_title="student")
                user_form_data.save()

                info_form_data.school = self.school
                info_form_data.user = user_form_data
                info_form_data.save()

                enrollment_form_data.student = info_form_data
                enrollment_form_data.academic_session = session
                enrollment_form_data.academic_term = term
                enrollment_form_data.academic_status = academic_status
                enrollment_form_data.save()

                messages.success(
                    request=request, message="Student Account has been created successfully!!")

                get_students(self, 'active', '')

            else:
                messages.error(request=request,
                               message="Fix Form Errors!!")

                get_students(self, 'active', '')

                return render(request=request, template_name=self.template_name, context={'form': self.form, 'user_form': user_form, 'info_form': info_form, 'enrollment_form': enrollment_form, 'object_list': self.object_list, 'all_student': self.all_student, 'add_student': self.add_student})

        else:

            get_students(self, '', 'active')
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")

        return render(request=request, template_name=self.template_name, context={'form': self.form, 'user_form': self.user_form, 'info_form': self.info_form, 'enrollment_form': self.enrollment_form(school=self.school), 'object_list': self.object_list, 'all_student': self.all_student, 'add_student': self.add_student})


class EditStudentPageView(LoginRequiredMixin, View):
    template_name = "backend/student/edit_student.html"

    user_form = EditUserForm
    info_form = StudentInformationForm
    enrollment_form = StudentEnrollmentForm

    def get(self, request, user_id):

        school = get_school(request)

        query_params = {
            'student_class': request.GET.get("student_class"),
            'academic_session': request.GET.get("academic_session"),
            'academic_status': request.GET.get("academic_status"),
        }

        url = f"{reverse('sch:students')}?{urlencode(query_params)}"

        try:
            user = User.objects.get(user_id=user_id)
            student_info = StudentInformation.objects.get(user=user)
            student_enrollment = StudentEnrollment.objects.get(
                student=student_info)

            context = {
                'user_form': self.user_form(instance=user),
                'info_form': self.info_form(instance=student_info),
                'enrollment_form': self.enrollment_form(instance=student_enrollment, school=school),
                'student_class': query_params['student_class'],
                'academic_session': query_params['academic_session'],
                'academic_status': query_params['academic_status']
            }

            return render(request=request, template_name=self.template_name, context=context)
        except User.DoesNotExist:
            messages.error(request=request,
                           message="Error getting student, Try Again!!")
            return redirect(url)
        except StudentInformation.DoesNotExist:
            messages.error(request=request,
                           message="Error getting student, Try Again!!")
            return redirect(url)
        except StudentEnrollment.DoesNotExist:
            messages.error(request=request,
                           message="Error getting student, Try Again!!")
            return redirect(url)

    def post(self, request, user_id):

        school = get_school(request)

        user = User.objects.get(user_id=user_id)
        student_info = StudentInformation.objects.get(user=user)
        student_enrollment = StudentEnrollment.objects.get(
            student=student_info)

        user_form = self.user_form(
            instance=user, data=request.POST, files=request.FILES)
        info_form = self.info_form(instance=student_info, data=request.POST)
        enrollment_form = self.enrollment_form(
            instance=student_enrollment, data=request.POST, school=school)

        query_params = {
            'student_class': request.POST.get("student_class"),
            'academic_session': request.POST.get("academic_session"),
            'academic_status': request.POST.get("academic_status"),
        }

        context = {
            'user_form': user_form,
            'info_form': info_form,
            'enrollment_form': enrollment_form,
            'student_class': query_params['student_class'],
            'academic_session': query_params['academic_session'],
            'academic_status': query_params['academic_status']
        }

        if user_form.is_valid() and info_form.is_valid() and enrollment_form.is_valid():

            user_form.save()
            info_form.save()
            enrollment_form.save()

            messages.success(
                request=request, message="Student Record Updated!!")

            url = f"{reverse('sch:students')}?{urlencode(query_params)}"
            return redirect(url)

        else:

            messages.error(request=request, message="Fix Form Errors!!")
            return render(request=request, template_name=self.template_name, context=context)


class SchoolFileUploadView(LoginRequiredMixin, ListView):

    school = None
    template_name = "backend/school/file_manager.html"

    def get_queryset(self):
        self.school = get_school(self.request)
        if self.school:
            return FilesManager.objects.filter(school=self.school).order_by('-date_created')
        return FilesManager.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SchoolFileUploadView, self).get_context_data(**kwargs)
        form = FilesManagerForm(school=self.school)

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

        self.object_list = self.get_queryset()
        form = FilesManagerForm(data=self.request.POST,
                                files=self.request.FILES, school=self.school)

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
                messages.success(
                    self.request, "File is been processed check details!!")

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


class UploadReportView(LoginRequiredMixin, View):
    template_name = "backend/student/upload_report.html"

    form = UploadReportForm

    # Context variables
    upload_report = ''
    view_report = ''

    def get(self, request):
        school = get_school(request)

        self.upload_report = 'active'
        self.view_report = ''

        return render(request=request, template_name=self.template_name, context={'form': self.form, 'upload_report': self.upload_report, 'view_report': self.view_report})


class SchoolClassesView(LoginRequiredMixin, ListView):

    model = SchoolClasses
    template_name = "backend/classes/school_classes.html"
    form = SchoolClassesForm

    def get_queryset(self):
        school = get_school(self.request)
        if school:
            return SchoolClasses.objects.filter(school_info=school).order_by('-date_created')
        return SchoolClasses.objects.none()

    def get_context_data(self, **kwargs):
        school = get_school(self.request)

        context = super(SchoolClassesView, self).get_context_data(**kwargs)

        context['form'] = self.form(school=school)

        return context

    def post(self, request, *args, **kwargs):

        school = get_school(request=request) #Get school info

        if 'create' in request.POST:

            form = self.form(request.POST, school=school)
            self.object_list = self.get_queryset()

            if form.is_valid():
                data = form.save(commit=False)
                data.school_info = school

                class_name = form.cleaned_data.get('class_name')

                data.save()
                messages.success(request, f"{class_name} successfully created")
                return redirect("sch:school_classes")

            else:
                # If form is invalid, re-render the page with errors
                context = self.get_context_data()
                context['form'] = form
                messages.error(request, form.errors.as_text())
                return self.render_to_response(context)

        elif 'delete' in request.POST:

            class_id = request.POST.get('class_id')

            try:
                SchoolClasses.objects.get(school_info=school, pk=class_id).delete()
                messages.success(
                    request, "Class has been deleted successfully!!")
            except SchoolClasses.DoesNotExist:
                messages.error(request, "Failed to delete class!!")

            return redirect('sch:school_classes')

        elif 'edit' in request.POST:

            class_id = request.POST.get('class_id')
            class_name = request.POST.get('class_name')


            try:
                school_class = SchoolClasses.objects.get(school_info=school, pk=class_id)
                school_class.class_name = class_name
                school_class.save()

                messages.success(
                    request, "Class has been updated successfully!!")
            except SchoolClasses.DoesNotExist:
                messages.error(request, "Failed to update class!!")
            except IntegrityError:
                messages.error(
                    request, f"Failed to update class: Class name '{class_name}' already exists!"
                )

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")

            return redirect('sch:school_classes')

        else:
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")
            return redirect('sch:school_classes')





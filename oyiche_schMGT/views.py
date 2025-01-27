# My Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import HttpResponse, JsonResponse
import pandas as pd
from urllib.parse import urlencode
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import Prefetch

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
                    is_current=True,
                    school_info=self.school,
                )
                status = request.POST.get('academic_status')
                print(f'STATUS: {status}')

                if status != 'None' and status !='' and status is not None:
                    academic_status = AcademicStatus.objects.get(
                        pk=request.POST.get('academic_status')
                    )

            query = {
                'student_class': student_class,
                'academic_session': academic_session,
            }

            if status != 'None' and status !='' and status is not None:
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
                messages.error(request, "Failed to delete account!!")
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

class SchoolSubjectView(LoginRequiredMixin, ListView):

    model = SchoolSubject
    template_name = "backend/classes/school_subject.html"
    form = SchoolSubjectForm

    def get_queryset(self):
        school = get_school(self.request)
        if school:
            return SchoolSubject.objects.filter(school_info=school).order_by('-date_created')
        return SchoolSubject.objects.none()

    def get_context_data(self, **kwargs):
        school = get_school(self.request)

        context = super(SchoolSubjectView, self).get_context_data(**kwargs)

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

                subject_name = form.cleaned_data.get('subject_name')

                data.save()
                messages.success(request, f"{subject_name} successfully created")
                return redirect("sch:school_subject")

            else:
                # If form is invalid, re-render the page with errors
                context = self.get_context_data()
                context['form'] = form
                messages.error(request, form.errors.as_text())
                return self.render_to_response(context)

        elif 'delete' in request.POST:

            subject_id = request.POST.get('subject_id')

            try:
                SchoolSubject.objects.get(school_info=school, pk=subject_id).delete()
                messages.success(
                    request, "Subject has been deleted successfully!!")
            except SchoolSubject.DoesNotExist:
                messages.error(request, "Failed to delete subject!!")

            return redirect('sch:school_subject')

        elif 'edit' in request.POST:

            subject_id = request.POST.get('subject_id')
            subject_name = request.POST.get('subject_name')


            try:
                school_subject = SchoolSubject.objects.get(school_info=school, pk=subject_id)
                school_subject.subject_name = subject_name
                school_subject.save()

                messages.success(
                    request, "Subject has been updated successfully!!")
            except SchoolSubject.DoesNotExist:
                messages.error(request, "Failed to update subject!!")
            except IntegrityError:
                messages.error(
                    request, f"Failed to update subject: Subject name '{school_subject.subject_name}' already exists!"
                )

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")

            return redirect('sch:school_subject')

        else:
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")
            return redirect('sch:school_subject')

class SubjectClassView(LoginRequiredMixin, ListView):

    model = SchoolClassSubjects
    template_name = "backend/classes/subject_class.html"
    form = SchoolClassSubjectForm

    def get_queryset(self, **kwargs):
        school = get_school(self.request)
        class_id = self.kwargs.get('class_id')
        if school:
            return SchoolClassSubjects.objects.filter(school_info=school, school_class=class_id).order_by('-date_created')
        return SchoolClassSubjects.objects.none()

    def get_context_data(self, **kwargs):
        school = get_school(self.request)
        class_id = self.kwargs.get('class_id')
        context = super(SubjectClassView, self).get_context_data(**kwargs)

        context['form'] = self.form(school=school, school_class=class_id)
        context['class_name'] = SchoolClasses.objects.get(pk=class_id).class_name
        context['class_id'] = SchoolClasses.objects.get(pk=class_id).pk


        return context

    def post(self, request, *args, **kwargs):

        school = get_school(request=request) #Get school info
        class_id = self.kwargs.get('class_id')
        class_name = SchoolClasses.objects.get(pk=class_id)


        if 'create' in request.POST:

            form = self.form(request.POST, school=school, school_class=class_id)

            self.object_list = self.get_queryset()

            if form.is_valid():
                data = form.save(commit=False)
                data.school_info = school
                data.school_class = class_name

                subject_name = form.cleaned_data.get('school_subject').subject_name

                data.save()
                messages.success(request, f"{subject_name.title()} has been assigned to {class_name.class_name.upper()}!")
                return redirect("sch:subject_class", class_id)

            else:
                # If form is invalid, re-render the page with errors
                context = self.get_context_data()
                context['form'] = form
                messages.error(request, form.errors.as_text())
                return self.render_to_response(context)

        elif 'delete' in request.POST:

            subject_id = request.POST.get('subject_id')

            try:
                school_subject = SchoolClassSubjects.objects.get(school_info=school, pk=subject_id)
                school_subject.delete()
                messages.success(
                    request, f"{school_subject.school_subject.subject_name.title()} has been removed from {class_name.class_name.upper()} successfully!")
            except SchoolClassSubjects.DoesNotExist:
                messages.error(request, "Failed to delete subject!")

            return redirect("sch:subject_class", class_id)


        else:
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")
            return redirect("sch:subject_class", class_id)

class SchoolGradesView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):

    model = SchoolGrades
    template_name = "backend/grades/school_grades.html"
    form = SchoolGradeForm


    def get_context_data(self, **kwargs):
        school = get_school(self.request)

        context = super(SchoolGradesView, self).get_context_data(**kwargs)

        context['form'] = self.form(school=school)

        return context

    def post(self, request):

        school = get_school(request=request) #Get school info

        form = SchoolGradeForm(request.POST, school=school)

        if form.is_valid():
            data = form.save(commit=False)
            data.school_info = school
            data.save()
            grade_letter = form.cleaned_data.get('grade_letter')
            messages.success(request, f"Grade: {grade_letter} successfully created!!")
            return redirect("sch:school_grade")
        else:
            # If form is invalid, re-render the page with errors
            messages.error(request, form.errors.as_text())
            return render(request=request, template_name=self.template_name, context={'form':form, 'school':school})

        return redirect("sch:school_grade")

class ListGradesView(LoginRequiredMixin, ListView):
    model = SchoolGrades
    template_name = "backend/grades/partials/grade_list.html"

    def get_queryset(self):
        school = get_school(self.request)
        if school:
            return SchoolGrades.objects.filter(school_info=school).order_by('-date_created')
        return SchoolGrades.objects.none()

class GradesEditView(LoginRequiredMixin, View):

    def get(self, request, grade_id):
        school = get_school(request)

        try:
            grade = SchoolGrades.objects.get(school_info=school, pk=grade_id)
            grade_form = SchoolGradeEditForm(instance=grade, school=school)

            return render(request=request, template_name="backend/grades/partials/grade_form.html", context={'form': grade_form, 'object': grade})
        except SchoolGrades.DoesNotExist:
            return JsonResponse({'error': 'Student Score not found!'}, status=404)

    def post(self, request, grade_id):

        school = get_school(request=request) #Get school info

        try:

            grade = SchoolGrades.objects.get(school_info=school, pk=grade_id)
            form = SchoolGradeEditForm(request.POST, instance=grade, school=school)

            if form.is_valid():
                form.save()
                grade_letter = form.cleaned_data.get('grade_letter')
                messages.success(request, f"Grade: {grade_letter} successfully edited!!")

            else:
                # If form is invalid, re-render the page with errors
                messages.error(request, form.errors.as_text())

        except SchoolGrades.DoesNotExist:
            messages.error(request, "Failed to edit grade!!")
        finally:
            return HttpResponse(status=204, headers={'Hx-Trigger':'listChanged'})

class GradesDeleteView(LoginRequiredMixin, View):

    def get(self, request, grade_id):
        school = get_school(request)

        try:
            grade = SchoolGrades.objects.get(school_info=school, pk=grade_id)
            grade_form = SchoolGradeEditForm(instance=grade, school=school)

            return render(request=request, template_name="backend/grades/partials/grade_delete.html", context={'form': grade_form, 'object': grade})

        except SchoolGrades.DoesNotExist:

            messages.error(request, "Grade not found!!")
            return redirect('sch:school_grade')

    def post(self, request, grade_id):

        school = get_school(request=request) #Get school info

        try:
            SchoolGrades.objects.get(school_info=school, pk=grade_id).delete()
            messages.success(
                request, "Grade has been deleted successfully!!")
        except SchoolGrades.DoesNotExist:
            messages.error(request, "Failed to delete grade!!")

        return HttpResponse(status=204, headers={'Hx-Trigger':' listChanged'})

class SchoolClassOptions(LoginRequiredMixin, View):
    template_name = "backend/classes/school_options.html"

    def get(self, request, class_id):
        school = get_school(request)

        try:
            class_id = SchoolClasses.objects.get(pk=class_id)
            return render(request=request, template_name=self.template_name, context={'school': school, 'object':class_id})
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

class ManageStudentSubjectGrades(LoginRequiredMixin, View):

    template_name = "backend/grades/manage_student_grades.html"
    form = UploadStudentSubjectGradeForm
    form2 = StudentScoreGradeForm
    form3 = GetStudentSubjectGradeForm

    # Context variables
    object_list = None
    grade_list = None
    all_student = ''
    add_student = ''
    manage_all = ''

    def get(self, request, class_id, subject_id=None):

        self.manage_all = 'active'
        self.all_student = ''
        self.add_student = ''

        self.school = get_school(request)
        self.form = self.form(school=self.school, school_class=class_id)
        self.form2 = self.form2(school=self.school, school_class=class_id)
        self.form3 = self.form3(school=self.school, school_class=class_id)

        if subject_id:
            self.grade_list = StudentScores.objects.filter(school_info=self.school, subject__school_subject=subject_id, session__is_current=True, term__is_current=True, subject__school_class=class_id).order_by('-average')

            self.grade_list = self.grade_list

        context = {
            'form': self.form,
            'form2': self.form2,
            'form3': self.form3,
            'manage_all': self.manage_all,
            'all_student': self.all_student,
            'add_student': self.add_student,
            'class_name': SchoolClasses.objects.get(pk=class_id),
            'grade_list': self.grade_list,
        }

        return render(request, template_name=self.template_name, context=context)

    def post(self, request, class_id, subject_id=None):

        self.school = get_school(request)
        class_name = SchoolClasses.objects.get(pk=class_id)

        if subject_id:
            self.grade_list = StudentScores.objects.filter(school_info=self.school, subject__school_subject=subject_id, session__is_current=True, term__is_current=True, subject__school_class=class_id).order_by('-average')

            self.grade_list = self.grade_list

        if 'upload_grade' in request.POST:

            form = self.form(data=request.POST, files=request.FILES, school=self.school, school_class=class_id)

            context = {
                'form': self.form(school=self.school, school_class=class_id),
                'form2': self.form2(school=self.school, school_class=class_id),
                'form3': self.form3(school=self.school, school_class=class_id),
                'all_student': 'active',
                'manage_all': self.manage_all,
                'add_student': self.add_student,
                'class_name': class_name,
                'object_list': self.object_list,
            }

            if form.is_valid():

                # Prepare for bulk create
                grade_list = []

                # Get uploaded file
                df = pd.read_excel(request.FILES['file'])

                # Get submitted session, term & subject
                session = AcademicSession.objects.get(school_info=self.school, is_current=True)
                term = AcademicTerm.objects.get(school_info=self.school, is_current=True)

                try:

                    subject = SchoolClassSubjects.objects.get(school_subject=request.POST.get('subject_name'), school_info=self.school, school_class=class_id)

                    highest_score = 0
                    lowest_score = float('inf')

                    # Pre-fetch all student data for efficiency
                    student_usernames = df.iloc[:,0].str.upper().tolist()
                    students = StudentInformation.objects.filter(user__username__in=student_usernames)
                    student_map = {student.user.username:student for student in students}

                    # Loop through the data
                    for _, row in df.iterrows():

                        ca1 = row.iloc[2]
                        ca2 = row.iloc[3]
                        ca3 = row.iloc[4]
                        exam = row.iloc[5]

                        username  = row.iloc[0].upper()
                        student = student_map[username]

                        if not student:
                            continue #Skip if student doesn't exist

                        score = StudentScores(
                            first_ca=ca1,
                            second_ca=ca2,
                            third_ca=ca3,
                            exam=exam,
                            student=student,
                            school_info=self.school,
                            session=session,
                            term=term,
                            subject=subject
                        )

                        # Perform calculation in memory
                        score.calculate_grade_and_total_score()
                        score.calculate_highest_and_lowest_score()

                        score.calculate_average()
                        score.calculate_positions()

                        # Update highest and lowest score dynamically
                        highest_score = max(score.total_score, highest_score)
                        lowest_score = min(score.total_score, lowest_score)

                        grade_list.append(score)

                    # Bulk create
                    with transaction.atomic():
                        StudentScores.objects.bulk_create(grade_list)

                    scores = StudentScores.objects.filter(
                        school_info=self.school,
                        session=session,
                        term=term,
                        subject=subject
                    )
                    scores.first().calculate_positions()
                    scores.update(
                        highest_score=highest_score,
                        lowest_score=lowest_score
                    )

                    messages.success(request, "Grades uploaded successfully!!")
                    # Return upload grades
                    self.object_list = StudentScores.objects.filter(school_info=self.school, session=session, term=term, subject=subject).order_by('-average')
                    context['object_list'] = self.object_list

                    return render(request, template_name=self.template_name, context=context)
                except SchoolClassSubjects.DoesNotExist:
                    messages.error(request, "Subject not found!!")

                    return render(request, template_name=self.template_name, context=context)

            else:
                messages.error(request=request, message=form.errors.as_text())

                context['form'] = form

                return render(request, template_name=self.template_name, context=context)

        elif 'single_upload' in request.POST:
            form2 = self.form2(data=request.POST, school=self.school, school_class=class_id)

            context = {
                'form': self.form(school=self.school, school_class=class_id),
                'form2': self.form2(school=self.school, school_class=class_id),
                'form3': self.form3(school=self.school, school_class=class_id),
                'all_student': '',
                'manage_all': '',
                'add_student': 'active',
                'class_name': class_name,
                'object_list': self.object_list,
            }

            if form2.is_valid():
                data = form2.save(commit=False)
                data.school_info = self.school

                try:

                    # Get submitted session, term & subject
                    session = AcademicSession.objects.get(school_info=self.school, is_current=True)
                    term = AcademicTerm.objects.get(school_info=self.school, is_current=True)

                    data.session = session
                    data.term = term

                    data.calculate_grade_and_total_score()
                    data.calculate_average()
                    data.save()
                    data.calculate_highest_and_lowest_score()
                    data.calculate_positions()

                    messages.success(request, "Grade uploaded successfully!!")

                    return render(request, template_name=self.template_name, context=context)

                except AcademicSession.DoesNotExist:
                    messages.error(request, "Academic Session not Found!!")
                except AcademicTerm.DoesNotExist:
                    messages.error(request, "Academic Term not found!!")

                return render(request, template_name=self.template_name, context=context)

            else:

                context['form2'] = form2
                return render(request, template_name=self.template_name, context=context)

        elif 'get_grades' in request.POST:

            form3 = self.form3(data=request.POST, school=self.school, school_class=class_id)

            context = {
                'form': self.form(school=self.school, school_class=class_id),
                'form2': self.form2(school=self.school, school_class=class_id),
                'form3': self.form3(school=self.school, school_class=class_id),
                'manage_all': 'active',
                'all_student': '',
                'add_student': self.add_student,
                'class_name': class_name,
                'object_list': self.object_list,
                'grade_list': self.grade_list,
            }

            if form3.is_valid():
                subject_name = form3.cleaned_data.get('subject_name').school_subject

                self.grade_list = StudentScores.objects.filter(school_info=self.school, subject__school_subject=subject_name, session__is_current=True, term__is_current=True, subject__school_class=class_id).order_by('-average')

                context['grade_list'] = self.grade_list

            else:

                context['form3'] = form3

            return render(request, template_name=self.template_name, context=context)

        messages.error(request=request, message="couldn't handle request, Try again!!")
        context = {
            'form': self.form(school=self.school, school_class=class_id),
            'form2': self.form2(school=self.school, school_class=class_id),
            'form3': self.form3(school=self.school, school_class=class_id),
            'manage_all': 'active',
            'all_student': '',
            'add_student': self.add_student,
            'class_name': SchoolClasses.objects.get(pk=class_id),
            'object_list': self.object_list,
        }

        return render(request, template_name=self.template_name, context=context)

class StudentScoreEditView(LoginRequiredMixin, View):

    def get(self, request, score_id):
        school = get_school(request)

        try:
            score = StudentScores.objects.get(school_info=school, pk=score_id)
            score_form = StudentScoreGradeEditForm(instance=score)

            return render(request=request, template_name="backend/grades/partials/score_form.html", context={'form': score_form, 'object': score})

        except StudentScores.DoesNotExist:

            return JsonResponse({'error': 'Student Score not found!'}, status=404)

    def post(self, request, score_id):
        school = get_school(request=request) #Get school info

        try:
            score = StudentScores.objects.get(school_info=school, pk=score_id)
            form = StudentScoreGradeEditForm(request.POST, instance=score)

            if form.is_valid():

                data = form.save(commit=False)
                data.calculate_grade_and_total_score()
                data.calculate_average()
                data.save()
                data.calculate_highest_and_lowest_score()
                data.calculate_positions()

                messages.success(request, f"{score.student.student_name}: score has been successfully edited!!")

            else:
                # If form is invalid, re-render the page with errors
                messages.error(request, form.errors.as_text())

            return redirect('sch:manage_student_grades', score.subject.school_class.pk, score.subject.school_subject.pk)

        except SchoolGrades.DoesNotExist:
            messages.error(request, "Student Grade not found Try Again!!")
            return redirect('sch:school_classes')

class StudentScoreDeleteView(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = 'auth:login'
    model = StudentScores
    success_message = ""

    def post(self, request, pk):

        school = get_school(request=request)
        subject = request.POST['subject']
        class_id = request.POST['class_id']

        try:
            # Delete the score
            score = StudentScores.objects.get(pk=pk, school_info=school)
            score.delete()

            # Success message
            messages.success(request, f"{score.student.student_name} {score.subject.school_subject.subject_name.title()} scores have been deleted successfully!")

            score.calculate_highest_and_lowest_score()
            score.calculate_positions()

            # Redirect to the appropriate URL using the object's details
            return redirect(reverse('sch:manage_student_grades', kwargs={
                'class_id': score.subject.school_class.pk,
                'subject_id': score.subject.school_subject.pk
            }))

        except StudentScores.DoesNotExist:

            messages.error(request, 'Failed to delete student score')

            return redirect(reverse('sch:manage_student_grades', kwargs={
                'class_id': class_id,
                'subject_id': subject
            }))

class ComputeResultView(LoginRequiredMixin, ListView):
    template_name = "backend/results/compute_result.html"
    model = StudentPerformance

    def get_queryset(self):
        school = get_school(self.request)
        class_id = self.kwargs.get('class_id')

        if school and class_id:

             # Get all subjects assigned to the class
            subjects = SchoolClassSubjects.objects.filter(
                school_info=school,
                school_class=class_id
            ).values_list('school_subject__subject_name', 'id',)



            # Get student performance with scores for each subject
            queryset = (
                StudentPerformance.objects.filter(
                    school_info=school,
                    current_enrollment__student_class=class_id,
                    current_enrollment__academic_session__is_current=True,
                    current_enrollment__academic_term__is_current=True,
                )
                .select_related('student', 'current_enrollment')
                .prefetch_related(
                    Prefetch(
                        'student__student_scores',
                        queryset=StudentScores.objects.filter(
                            school_info=school,
                            term__is_current=True,
                            session__is_current=True,
                        )
                    )
                )
                .order_by('-student_average')
            )

            return queryset, subjects

        return StudentPerformance.objects.none(), []


    def get_context_data(self, **kwargs):
        class_id = self.kwargs.get('class_id', '')
        context = super().get_context_data(**kwargs)

        queryset, subjects = self.get_queryset()
        context['queryset'] = queryset
        context['subjects'] = subjects
        context["class_name"] = SchoolClasses.objects.get(pk=class_id)
        context['academic_session'] = AcademicSession.objects.filter(is_current=True).first()
        context['academic_term'] = AcademicTerm.objects.filter(is_current=True).first()
        return context

    def post(self, request, class_id):

        # All required variables
        academic_term = AcademicTerm.objects.filter(is_current=True).first()
        academic_session = AcademicSession.objects.filter(is_current=True).first()
        class_detail = SchoolClasses.objects.get(pk=class_id)
        school = get_school(self.request)

        def perform_computation(which, student_performance_list):

            # Create performances and calculate student averages
            with transaction.atomic():
                # Bulk create student performances

                if which == 'compute':
                    performances = StudentPerformance.objects.bulk_create(student_performance_list)

                if which == 're-compute':
                    performances = student_performance_list

                # Calculate student averages and other individual data
                for performance in performances:
                    performance.calculate_student_average_total_marks_total_subject()

                # Bulk update all student-related fields
                StudentPerformance.objects.bulk_update(
                    performances,
                    ['total_marks_obtained', 'total_subject', 'student_average']
                )

                # Calculate class averages after all student averages are ready
                for performance in performances:
                    performance.calculate_class_average()

                # Bulk update all class average fields
                StudentPerformance.objects.bulk_update(
                    performances,
                    ['class_average']
                )

                # Calculate term positions
                first_performance = StudentPerformance.objects.filter(
                    school_info=school,
                    current_enrollment__student_class=class_detail,
                    current_enrollment__academic_term=academic_term,
                    current_enrollment__academic_session=academic_session
                ).first()


                if first_performance: first_performance.calculate_term_position()



        # List to hold the student performance instance for bulk creation
        student_performance_list = []

        # Get all students enrolled in the class
        enrolled_class = StudentEnrollment.objects.filter(
            academic_session=academic_session,
            academic_term=academic_term,
            student_class=class_detail,
            academic_status__status="active",
        )

        # Validate if student exist in the enrolled class
        if not enrolled_class:
            messages.error(request, f"No student enrolled into {class_detail.class_name.upper()} class!!")
            return redirect('sch:compute_results', class_id)

        if 'compute' in request.POST:

            # Create Performance for each student
            student_performance_list = [
                StudentPerformance(
                    school_info=school,
                    student=student.student,
                    current_enrollment=student
                )
                for student in enrolled_class
            ]

            perform_computation(which='compute', student_performance_list=student_performance_list)

            messages.success(request=request, message=f'computation successful!')
            return redirect('sch:compute_results', class_id)

        elif 're-compute' in request.POST:
            # Create Performance for each student
            student_performance_list = StudentPerformance.objects.filter(
                school_info=school,
                current_enrollment__student_class=class_detail,
                current_enrollment__academic_term=academic_term,
                current_enrollment__academic_session=academic_session,
            )

            perform_computation(which='re-compute', student_performance_list=student_performance_list)

            messages.success(request=request, message=f'computation successful!')
            return redirect('sch:compute_results', class_id)


        messages.error(request=request, message="Couldn't handle request, Try again!!")
        return redirect('sch:compute_results', class_id)






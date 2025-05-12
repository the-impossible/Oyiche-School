from oyiche_schMGT.imports import *
from oyiche_schMGT.views import get_school
# from oyiche_schMGT.students.forms import *

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
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

        try:

            # Extract filtering parameters
            student_class = request.GET.get("student_class")
            school_academic_session = AcademicSession.objects.get(school_info=self.school, is_current=True)
            school_academic_term = AcademicTerm.objects.get(school_info=self.school, is_current=True)
            academic_status = AcademicStatus.objects.get(status="active")

            query = {}

            # Prepare initial values for the form
            initial_data = {}

            # Filter students if parameters exist
            if student_class and student_class != 'None':
                query["student_class"] = student_class
                query['academic_session'] = school_academic_session
                query['academic_term'] = school_academic_term
                query['academic_status'] = academic_status
                query['studennt__school'] = self.school
                initial_data['student_class'] = student_class

            if query:
                self.object_list = StudentEnrollment.objects.filter(**query)
                self.form = self.form(initial=initial_data, school=self.school)
            else:
                self.form = self.form(school=self.school)

        except AcademicSession.DoesNotExist:
            messages.error(request, "Academic session not found.")
        except AcademicTerm.DoesNotExist:
            messages.error(request, "Academic term not found.")
        except AcademicStatus.DoesNotExist:
            messages.error(request, "Academic status not found.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return render(request=request, template_name=self.template_name, context={'form': self.form, 'user_form': self.user_form, 'info_form': self.info_form, 'enrollment_form': self.enrollment_form(school=self.school), 'object_list': self.object_list, 'all_student': self.all_student, 'add_student': self.add_student})

    def post(self, request):

        self.school = get_school(request)

        form = self.form(data=request.POST, school=self.school)

        def get_students(self, add_student, all_student, student_class=None):

            nonlocal form
            try:
                student_class = form.cleaned_data.get('student_class')
            except AttributeError:
                student_class = student_class
            school_academic_session = AcademicSession.objects.get(school_info=self.school, is_current=True)
            school_academic_term = AcademicTerm.objects.get(school_info=self.school, is_current=True)
            academic_status = AcademicStatus.objects.get(status="active")

            query = {
                'student_class': student_class,
                'academic_session': school_academic_session,
                'academic_term': school_academic_term,
                'academic_status': academic_status,
                'student__school': self.school,
            }

            student_in_class_and_in_session = StudentEnrollment.objects.filter(
                **query).order_by('-date_created')

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

                student_class = request.POST.get('student_class')
                get_students(self, 'active', '', student_class)


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

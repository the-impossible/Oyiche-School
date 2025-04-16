from oyiche_schMGT.imports import *
from oyiche_schMGT.views import get_school
from oyiche_schMGT.enrollments.forms import *
from django.db.models import Q

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ManageStudentEnrollment(LoginRequiredMixin, View):

    template_name = "backend/enrollment/manage_enrollment.html"
    form = EnrollmentRequestForm
    form2 = EnnrollmentMigrationForm

    # Context variables
    object_list = None
    context = {}
    manage_enrollement = ''
    migrate_enrollment = ''

    @method_decorator(has_updated)
    def get(self, request):

        self.manage_enrollement = 'active'
        self.migrate_enrollment = ''

        self.school = get_school(request)

        # Extract filtering parameters
        student_class = request.GET.get("student_class")
        academic_session = request.GET.get("academic_session")
        academic_term = request.GET.get("academic_term")
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

        self.form2 = self.form2(school=self.school)

        self.context = {
            'form': self.form,
            'form2': self.form2,
            'object_list': self.object_list,
            'manage_enrollement': self.manage_enrollement,
            'migrate_enrollment': self.migrate_enrollment,
        }

        return render(request=request, template_name=self.template_name, context=self.context)


    @method_decorator(has_updated)
    def post(self, request):

        self.school = get_school(request)

        form = self.form(data=request.POST, school=self.school)
        form2 = self.form2(school=self.school)

        school_academic_session = AcademicSession.objects.filter(is_current=True, school_info=self.school).first()
        school_academic_term = AcademicTerm.objects.filter(is_current=True, school_info=self.school).first()

        def get_enrollment():

            nonlocal form
            data = form.cleaned_data

            query = {
                'student_class': data.get('student_class'),
                'academic_session': data.get('academic_session'),
                'academic_status': data.get('academic_status'),
                'academic_term': data.get('academic_term'),
                'student__school': self.school,
            }

            student_enrollment = StudentEnrollment.objects.filter(
                **query).order_by('-date_created')

            self.object_list = student_enrollment
            self.form = form

            self.manage_enrollement = 'active'
            self.migrate_enrollment = ''

        def migrate_enrollment(form):

            selected_ids = request.POST.getlist('selected_ids')

            if not selected_ids:
                messages.error(request, "No students selected for migration.")
                return

            student_class = form.cleaned_data.get('student_class')
            academic_session = form.cleaned_data.get('academic_session')
            academic_status = form.cleaned_data.get('academic_status')

            current_enrollments = StudentEnrollment.objects.filter(enrollment_id__in=selected_ids)

            if not current_enrollments.exists():
                messages.error(request, "Selected enrollments could not be found.")
                return

            current_academic_term = current_enrollments.first().academic_term.term.lower()
            current_academic_session = current_enrollments.first().academic_session.session.lower()
            current_academic_status = current_enrollments.first().academic_status.status.lower()

            school_current_session = school_academic_session.session.lower()
            school_current_term = school_academic_term.term.lower()

            statuses = AcademicStatus.objects.filter(status__in=["completed", "active"])
            completed_status = statuses.get(status="completed")
            active_status = statuses.get(status="active")

            # Handle Migration to Same Term

            # Handing Inactive to Inactive
            if current_academic_status == 'inactive' and academic_status.status.lower() == 'inactive':
                messages.error(request, "selected enrollment is already marked as inactive")
                return

            # (Active | Completed) to Inactive
            if academic_status.status.lower() == 'inactive' and (current_academic_status == 'active' or current_academic_status == 'completed'):

                in_active_status = AcademicStatus.objects.get(status="inactive")

                if current_academic_status == 'active':

                    with transaction.atomic():

                        # Bulk update current enrollments
                        current_enrollments.update(academic_status=in_active_status, promoted_class=student_class)

                        messages.success(request, f"{len(current_enrollments)} student enrollment status has been updated successfully.")
                        return

                elif current_academic_status == 'completed':
                    # Get student IDs from the current enrollments
                    selected_active = [active_id.student.student_id for active_id in current_enrollments]

                    # Query the actual active enrollments (not just check existence)
                    active_enrollments = StudentEnrollment.objects.filter(
                        student__student_id__in=selected_active,
                        academic_status=active_status
                    )

                    if active_enrollments.exists():

                        messages.success(request, f"Active record exist for the selected enrollment, kindly update the active records to inactive.")

                    else:

                        with transaction.atomic():

                            # Bulk update current enrollments
                            current_enrollments.update(academic_status=in_active_status, promoted_class=student_class)

                            messages.success(request, f"{len(current_enrollments)} student enrollment status has been updated successfully.")
                            return

            # Handling Completed to Completed:
            if current_academic_status == 'completed' and academic_status.status.lower() == 'completed':
                # Get student IDs from the current enrollments
                selected_active = [active_id.student.student_id for active_id in current_enrollments]

                # Query the actual active enrollments (not just check existence)
                active_enrollments = StudentEnrollment.objects.filter(
                    student__student_id__in=selected_active,
                    academic_status=active_status
                )

                if active_enrollments.exists():

                    messages.error(request, f"Active record exist for the selected enrollment, kindly update the active records to inactive.")
                    return

            # Handle term progression
            if current_academic_term == "first term":

                if school_current_term != "second term":
                    messages.error(
                        request,
                        "When migrating from first term, the new academic term must be 'second term' kindly update school term."
                    )
                    return

            elif current_academic_term == "second term":

                if school_current_term != "third term":
                    messages.error(
                        request,
                        "When migrating from second term, the new academic term must be 'third term' kindly update school term."
                    )
                    return

            elif current_academic_term == "third term":

                if school_current_session == current_academic_session:
                    messages.error(
                        request,
                        "Migration from the third term is not allowed in the same session. Please change to a new session."
                    )
                    return

                if school_current_term != "first term":
                    messages.error(
                        request,
                        "When migrating from the third term, the new academic term must be 'first term' kindly update school term."
                    )
                    return
            else:
                messages.error(
                    request,
                    "update to the valid term."
                )
                return

            # Handle (Completed | Active) to Active
            if (current_academic_status == 'completed' or current_academic_status == 'active') and (academic_status.status.lower() == 'completed' or academic_status.status.lower() == 'inactive'):
                # Get student IDs from the current enrollments
                selected_active = [active_id.student.student_id for active_id in current_enrollments]

                # Query enrollments that exist in other classes (exclude current class)
                existing_enrollment = StudentEnrollment.objects.filter(
                    student__student_id__in=selected_active
                ).exclude(student_class=student_class)

                if existing_enrollment.exists():
                    if school_academic_session == current_academic_session:
                        messages.error(request, "Invalid enrollment, migration is to a previously enrolled class.")
                        return


            # (Inactive | Completed | Active ) to Completed
            with transaction.atomic():

                # Bulk update current enrollments
                current_enrollments.update(academic_status=completed_status, promoted_class=student_class)

                # Prepare new enrollment
                new_enrollments = []

                for enrollment in current_enrollments:
                    new_enrollment = StudentEnrollment(
                        student=enrollment.student,
                        student_class=student_class,
                        academic_session=school_academic_session,
                        academic_term=school_academic_term,
                        academic_status=active_status,
                    )
                    new_enrollments.append(new_enrollment)

                # Bulk create new enrollments
                StudentEnrollment.objects.bulk_create(new_enrollments)

                messages.success(request, f"{len(new_enrollments)} students migrated successfully.")
                return

        def delete_enrollment():

            selected_ids = request.POST.getlist('selected_ids')

            if not selected_ids:
                messages.error(request, "No enrolllment selected for deletion.")
                return

            enrollments_to_delete = StudentEnrollment.objects.filter(enrollment_id__in=selected_ids)

            # Check if the selected enrollments exist
            if not enrollments_to_delete.exists():
                messages.error(request, "Selected enrollments could not be found.")
                return

            current_academic_status =  enrollments_to_delete.first().academic_status.status.lower()

            # Check if the enrollment_to_delete is completed
            if current_academic_status == 'completed' or current_academic_status == 'inactive':
                messages.error(request, "completed and inactive enrollment cannot be deleted")
                return

            with transaction.atomic():
                count, _ = enrollments_to_delete.delete()

            messages.success(request, f"{count} enrollments have been deleted successfully.")

        if 'get_enrollment' in request.POST:

            if form.is_valid():
                get_enrollment()
            else:
                messages.error(request=request, message=form.errors.as_text())

            self.context = {
                'form': self.form,
                'form2': form2,
                'object_list': self.object_list,
                'manage_enrollement': self.manage_enrollement,
                'migrate_enrollment': self.migrate_enrollment,
                'school_academic_session': school_academic_session,
                'school_academic_term': school_academic_term,
            }

        elif 'migrate_enrollment' in request.POST:

            form2 = self.form2(data=request.POST, school=self.school)

            if form2.is_valid():

                migrate_enrollment(form2)
                self.manage_enrollement = 'active'

                initial_data = {
                    'student_class': request.POST.get('get_student_class'),
                    'academic_session': request.POST.get('get_academic_session'),
                    'academic_term': request.POST.get('get_academic_term'),
                    'academic_status': request.POST.get('get_academic_status'),
                }

                student_enrollment = StudentEnrollment.objects.filter(
                **initial_data).order_by('-date_created')

                self.object_list = student_enrollment

                self.context = {
                    'form': self.form(initial=initial_data, school=self.school),
                    'form2': form2,
                    'object_list': self.object_list,
                    'manage_enrollement': self.manage_enrollement,
                    'migrate_enrollment': self.migrate_enrollment,
                    'school_academic_session': school_academic_session,
                    'school_academic_term': school_academic_term,
                }

            else:
                messages.error(request=request, message=form2.errors.as_text())

        elif 'delete_enrollment' in request.POST:

            delete_enrollment()
            self.manage_enrollement = 'active'

            initial_data = {
                'student_class': request.POST.get('get_student_class'),
                'academic_session': request.POST.get('get_academic_session'),
                'academic_term': request.POST.get('get_academic_term'),
                'academic_status': request.POST.get('get_academic_status'),
            }

            student_enrollment = StudentEnrollment.objects.filter(
            **initial_data).order_by('-date_created')

            self.object_list = student_enrollment

            self.context = {
                'form': self.form(initial=initial_data, school=self.school),
                'form2': form2,
                'object_list': self.object_list,
                'manage_enrollement': self.manage_enrollement,
                'migrate_enrollment': self.migrate_enrollment,
                'school_academic_session': school_academic_session,
                'school_academic_term': school_academic_term,
                }

        else:

            messages.error(request=request,
                           message="couldn't handle request, Try again!!")

        return render(request=request, template_name=self.template_name, context=self.context)

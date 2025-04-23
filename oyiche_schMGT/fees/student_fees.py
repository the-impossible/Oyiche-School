from oyiche_schMGT.imports import *
from oyiche_schMGT.views import get_school
from oyiche_schMGT.fees.forms import *
from django.contrib import messages

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ExportFeeTemplateView(LoginRequiredMixin, View):

    @method_decorator(has_updated)
    def get(self, request, class_id):

        # All required variables
        school = get_school(self.request)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=school)
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        academic_term = AcademicTerm.objects.filter(is_current=True, school_info=school).first()
        academic_session = AcademicSession.objects.filter(is_current=True, school_info=school).first()
        class_detail = class_name
        return self.export_fees_template(request, class_detail, academic_session, academic_term, school)

    @method_decorator(has_updated)
    def export_fees_template(self, request, class_detail, academic_session, academic_term, school_info):

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{class_detail} Fees Template"

        # Header row
        ws.append([
            "Student ID",
            "Name",
            "Status",
        ])

        # Get all students enrolled in the class
        enrolled_class = StudentEnrollment.objects.filter(
            academic_session=academic_session,
            academic_term=academic_term,
            student_class=class_detail,
            academic_status__status="active",
            student__school=school_info,
        )

        # Validate if student exist in the enrolled class
        if not enrolled_class:
            messages.error(request, f"No student enrolled into {class_detail.class_name.upper()} class!!")
            return redirect('sch:manage_student_fees', class_detail.pk)

        for student in enrolled_class:

            if student.has_paid:
                fees_status = 'paid'
            else:
                fees_status = 'unpaid'

            # Append student data to the worksheet
            ws.append(
                [
                    str(student.student.user),
                    str(student.student.student_name),
                    fees_status,
                ]
            )

        # Return Excel file as response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{class_detail.class_name.upper()}_Fees_Template".xlsx'
        wb.save(response)
        return response

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ManageStudentFees(LoginRequiredMixin, View):

    template_name = "backend/fees/manage_student_fees.html"
    form = UploadStudentFeeForm

    # Context variables
    object_list = None

    @method_decorator(has_updated)
    def get(self, request, class_id):

        self.school = get_school(request)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=self.school)
            school_academic_session = AcademicSession.objects.get(school_info=self.school, is_current=True)
            school_academic_term = AcademicTerm.objects.get(school_info=self.school, is_current=True)
            academic_status = AcademicStatus.objects.get(status="active")
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        self.object_list = StudentEnrollment.objects.filter(student_class=class_name, student__school=self.school, academic_session=school_academic_session, academic_status=academic_status, academic_term=school_academic_term).order_by('-date_created')

        context = {
            'form': self.form,
            'class_name': class_name,
            'object_list': self.object_list,
        }

        return render(request, template_name=self.template_name, context=context)

    @method_decorator(has_updated)
    def post(self, request, class_id):

        self.school = get_school(request)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=self.school)
            school_academic_session = AcademicSession.objects.get(school_info=self.school, is_current=True)
            school_academic_term = AcademicTerm.objects.get(school_info=self.school, is_current=True)
            academic_status = AcademicStatus.objects.get(status="active")
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        if 'bulk_upload' in request.POST:

            form = self.form(files=request.FILES)

            context = {
                'form': self.form(),
                'class_name': class_name,
                'object_list': self.object_list,
            }

            if form.is_valid():

                # Prepare for bulk create
                fees_list = []

                # Get uploaded file
                df = pd.read_excel(request.FILES['file'])

                try:

                    # Pre-fetch all student data for efficiency
                    student_usernames = df.iloc[:,0].str.upper().tolist()
                    students_enrollment = StudentEnrollment.objects.filter(academic_session=school_academic_session, academic_status=academic_status, academic_term=school_academic_term, student__user__username__in=student_usernames)

                    enrollment_map = {student.student.user.username:student for student in students_enrollment}

                    # Loop through the data
                    for _, row in df.iterrows():

                        username  = row.iloc[0].upper()
                        fee_status = row.iloc[2].strip().lower()

                        enrollment = enrollment_map[username]
                        if not enrollment:
                            continue #Skip if enrollment doesn't exist

                        enrollment.has_paid = fee_status == 'paid'
                        fees_list.append(enrollment)

                    # Bulk update
                    if fees_list:

                        with transaction.atomic():
                            StudentEnrollment.objects.bulk_update(fees_list, ['has_paid'])
                        messages.success(request, "Fees status updated successfully!!")
                    else:
                        messages.warning(request, "No matching student enrollment found to update!!")

                    self.object_list = StudentEnrollment.objects.filter(student_class=class_name, student__school=self.school, academic_session=school_academic_session, academic_status=academic_status, academic_term=school_academic_term).order_by('-date_created')
                    context['object_list'] = self.object_list

                except Exception as e:
                    messages.error(request, f"Error occurred: {str(e)}")

                return render(request, template_name=self.template_name, context=context)

            else:
                messages.error(request=request, message=form.errors.as_text())

                context['form'] = form

                return render(request, template_name=self.template_name, context=context)

        messages.error(request=request, message="couldn't handle request, Try again!!")
        context = {
            'form': self.form,
            'class_name': class_name,
            'object_list': self.object_list,
        }

        return render(request, template_name=self.template_name, context=context)

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ListStudentFeesView(LoginRequiredMixin, ListView):
    model = StudentEnrollment
    template_name = "backend/fees/fees_list.html"

    def get_queryset(self):

        self.school = get_school(self.request)
        class_id = self.kwargs.get('class_id')

        try:

            class_name = SchoolClasses.objects.get(pk=class_id, school_info=self.school)
            school_academic_session = AcademicSession.objects.get(school_info=self.school, is_current=True)
            school_academic_term = AcademicTerm.objects.get(school_info=self.school, is_current=True)
            academic_status = AcademicStatus.objects.get(status="active")

            return StudentEnrollment.objects.filter(student_class=class_name, student__school=self.school, academic_session=school_academic_session, academic_status=academic_status, academic_term=school_academic_term).order_by('-date_created')

        except SchoolClasses.DoesNotExist:
            return StudentEnrollment.objects.none()

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class StudentFeeEditView(LoginRequiredMixin, View):

    def get(self, request, enrollment_id):
        school = get_school(request)

        try:
            enrollment = StudentEnrollment.objects.get(student__school=school, pk=enrollment_id)
            enrollment_form = SchoolFeeEditForm(instance=enrollment)

            return render(request=request, template_name="backend/fees/fee_edit_form.html", context={'form': enrollment_form, 'object': enrollment})

        except StudentEnrollment.DoesNotExist:
            return JsonResponse({'error': 'Student Enrollment not found!'}, status=404)

    def post(self, request, enrollment_id):

        school = get_school(request=request) #Get school info

        try:

            enrollment = StudentEnrollment.objects.get(student__school=school, pk=enrollment_id)
            form = SchoolFeeEditForm(request.POST, instance=enrollment)

            if form.is_valid():

                form.save()
                messages.success(request, f"Student fee status has been updated successfully!!")

            else:
                # If form is invalid, re-render the page with errors
                messages.error(request, form.errors.as_text())

        except StudentEnrollment.DoesNotExist:
            messages.error(request, "Failed to edit student fee status!!")
        finally:
            return HttpResponse(status=204, headers={'Hx-Trigger':'listChanged'})
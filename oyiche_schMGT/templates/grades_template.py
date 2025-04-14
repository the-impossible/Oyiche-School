from oyiche_schMGT.imports import *
from oyiche_schMGT.views import get_school


@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ExportGradeTemplateView(LoginRequiredMixin, View):
    template_name = "backend/results/compute_result.html"
    model = StudentEnrollment

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
        return self.export_grade_template(request, class_detail, academic_session, academic_term)

    def export_grade_template(self, request, class_detail, academic_session, academic_term):

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{class_detail} Grade Template"

        # Header row
        ws.append([
            "Student ID",
            "Name",
            "CA1",
            "CA2",
            "CA3",
            "Exam"
        ])

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
            return redirect('sch:manage_student_grades', class_detail.pk)

        for student in enrolled_class:
            ws.append(
                [
                    str(student.student.user),
                    str(student.student.student_name),
                    '',
                    '',
                    '',
                    '',
                ]
            )

        # Return Excel file as response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{class_detail.class_name.upper()}_Grade_Template".xlsx'
        wb.save(response)
        return response


from django.db.models import Max
from oyiche_schMGT.models import *
from oyiche_payment.models import *
from oyiche_schMGT.views import get_school

def global_dashboard_context(request):
    if not request.user.is_authenticated:
        return {}

    school = get_school(request)

    academic_term = AcademicTerm.objects.filter(is_current=True, school_info=school).first()
    academic_session = AcademicSession.objects.filter(is_current=True, school_info=school).first()
    academic_status = AcademicStatus.objects.filter(status='active').first()

    context = {}
    if school:
        student_info = StudentInformation.objects.filter(school=school)
        current_enrollment_total = StudentEnrollment.objects.filter(
            academic_session=academic_session,
            academic_term=academic_term,
            academic_status=academic_status,
        ).count()
        context['total_students'] = current_enrollment_total
        context['total_classes'] = SchoolClasses.objects.filter(school_info=school).count()
        context['total_subjects'] = SchoolSubject.objects.filter(school_info=school).count()
        context['total_admins'] = SchoolAdminInformation.objects.filter(school=school).count()
        context['new_student_list'] = student_info.order_by('-date_created')[:10]

        # Get the highest student_average for each class
        top_avg_per_class = (
            StudentPerformance.objects.filter(school_info=school)
            .values('current_enrollment__student_class')
            .annotate(max_average=Max('student_average'))
        )

        # Get the actual students with the highest average in each class
        exam_toppers = StudentPerformance.objects.filter(
            school_info=school,
            student_average__in=[entry['max_average'] for entry in top_avg_per_class]
        ).select_related('student', 'current_enrollment__student_class')

        context['exam_toppers'] = exam_toppers

    return context

def global_payment_context(request):
    if not request.user.is_authenticated:
        return {}

    school = get_school(request)

    context = {}

    if school:

        school_unit = SchoolUnit.objects.filter(school=school).first()
        # get current unit
        context['available_unit'] = school_unit.available_unit if school_unit else 0
        # get total unit purchased
        context['total_unit'] = school_unit.total_unit if school_unit else 0

        # unit used this term
        academic_session = AcademicSession.objects.filter(school_info=school, is_current=True).first()
        academic_term = AcademicTerm.objects.filter(school_info=school, is_current=True).first()

        unit_used = UnitUsedByTerm.objects.filter(school=school, academic_session=academic_session, academic_term=academic_term).first()
        context['unit_used'] = unit_used.unit_used if unit_used else 0

        # last amount paid
        payment_history = SchoolPaymentHistory.objects.filter(school=school, payment_status='success').order_by('-created_at')

        if payment_history.exists():
            context['last_amount_paid'] = payment_history.first().amount_paid
        else:
            context['last_amount_paid'] = 0

        # payment history
        payment_history = SchoolPaymentHistory.objects.filter(school=school).order_by('-created_at')[:10]
        context['payment_list'] = payment_history

    return context

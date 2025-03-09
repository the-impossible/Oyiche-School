from django.db.models import Max
from oyiche_schMGT.models import *
from oyiche_schMGT.views import get_school

def global_dashboard_context(request):
    if not request.user.is_authenticated:
        return {}

    school = get_school(request)

    context = {}
    if school:
        student_info = StudentInformation.objects.filter(school=school)
        context['total_students'] = student_info.count()
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

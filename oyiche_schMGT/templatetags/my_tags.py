from django import template

register = template.Library()

@register.filter
def get_score_for_subject(student_scores, subject_id):
    # Iterate over the prefetched student_scores
    for score in student_scores:
        if score.subject.id == subject_id:
            return score
    return None  # Return None if no matching score is found

@register.filter
def get_score_for_each_studennt_subject(student_scores, subject_id):
    # Iterate over the prefetched student_scores
    for score in student_scores:
        if score.subject.id == subject_id:
            return score
    return None  # Return None if no matching score is found

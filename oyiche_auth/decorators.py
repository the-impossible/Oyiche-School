# My django imports
from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from oyiche_schMGT.models import *
from oyiche_schMGT import views

# My app imports
# Determining if the user is an admin
def is_staff(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return func(request, *args, **kwargs)
            else:
                messages.warning(request, 'You are not authorized to view that page')
                return redirect('auth:dashboard')
    return wrapper_func

# Determining if the user is a school
def is_school(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if str(request.user.userType).lower() == 'school':
                return func(request, *args, **kwargs)
            else:
                messages.warning(request, 'You are not authorized to view this page')
                return redirect('auth:dashboard')

        # If the user is not authenticated, redirect to login page
        messages.warning(request, 'Please log in to access this page')
        return redirect('auth:login')

    return wrapper_func

# Determine if user has updated their account or account
def has_updated(func):
    def wrapper_func(request, *args, **kwargs):

        if str(request.user.userType) == 'school':

            school_info =  views.get_school(request)

            if school_info:

                academic_session = AcademicSession.objects.filter(school_info=school_info, is_current=True)
                academic_term = AcademicTerm.objects.filter(school_info=school_info, is_current=True)
                school_details = SchoolInformation.objects.filter(sch_id=school_info.pk).first()

                if school_details.school_updated and academic_session.exists() and academic_term.exists():
                    return func(request, *args, **kwargs)

                else:
                    messages.info(request, 'You have to update your school detail before proceeding!')
                    return redirect('sch:manage_school_details')
            else:
                messages.info(request, 'School Profile not found!')
                return redirect('auth:dashboard')

    return wrapper_func

# Determine if student has paid fess for the current session and term
def has_paid(func):
    def wrapper_func(request, *args, **kwargs):

        session = Session.objects.filter(is_current=True).first()
        payment = Payments.objects.filter(student=request.user, status="success", session=session).exists()

        if payment:
            return func(request, *args, **kwargs)
        else:
            messages.warning(request, 'You have no payment record, for this current session and term, kindly contact school admin')
            return redirect('auth:dashboard')

    return wrapper_func
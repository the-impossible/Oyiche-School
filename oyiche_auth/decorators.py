# My django imports
from django.contrib.auth.models import AnonymousUser
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages

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
            if request.user.userType == 'school':
                return func(request, *args, **kwargs)
            else:
                messages.warning(request, 'You are not authorized to view this page')
                return redirect('auth:dashboard')
    return wrapper_func

# Determine if user has updated their account or account
def has_updated(func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.has_updated():
            return func(request, *args, **kwargs)
        else:
            messages.info(request, 'You have to update your profile before proceeding!')
            return redirect('auth:manage_profile', request.user.user_id)
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
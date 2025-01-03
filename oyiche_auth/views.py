from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# My app imports
from oyiche_schMGT.models import *

# Create your views here.


class RegisterView(TemplateView):
    template_name = "backend/auth/register.html"


class LoginView(TemplateView):
    template_name = "backend/auth/login.html"


class LoginView(View):
    def get(self, request):
        return render(request, 'backend/auth/login.html')

    def post(self, request):
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        if username and password:
            # Authenticate user
            user = authenticate(
                request, username=username.upper(), password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'You are now signed in {user}')
                    nxt = request.GET.get('next', None)

                    if nxt is None:
                        return redirect('auth:dashboard')
                    return redirect(self.request.GET.get('next', None))
                else:
                    messages.warning(
                        request, 'Account not active contact the administrator')
                    return redirect('auth:login')
            messages.warning(request, 'Invalid login credentials')
            return redirect('auth:login')
        else:
            messages.error(request, 'All fields are required!!')
            return redirect('auth:login')


class ForgotPasswordView(TemplateView):
    template_name = "backend/auth/forgot-password.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "backend/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        return context

def custom_404_view(request, exception=None):
    error_message = str(exception) if exception else "Page not found"
    return render(request, "404.html", {"error_message": error_message}, status=404)

class LogoutView(LoginRequiredMixin, View):
    login_url = 'auth:login'
    def post(self, request):
        logout(request)
        messages.success(request, 'You are successfully logged out, to continue login again')
        return redirect('auth:login')
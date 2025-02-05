from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# My app imports
from oyiche_schMGT.models import *
from oyiche_auth.forms import *

# Create your views here.


class RegisterView(View):
    template_name = "backend/auth/register.html"
    form = SchoolForm

    def get(self, request):
        context = {
            'form': self.form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form(request.POST)

        if form.is_valid():
            data = form.save(commit=False)
            email = form.clean_email()

            # Validate password
            password = form.clean_password()
            password1 = request.POST.get('password1')

            if password == password1:

                data.userType = UserType.objects.get_or_create(user_title='school')[0]
                data.save()
                SchoolInformation.objects.create(
                    principal_id=data,
                    school_email=email
                )
                messages.success(request, "Account created successfully, You can login now")
                return redirect('auth:login')
            else:
                messages.error(request, "password and confirm password doesn't match")

                return render(request, self.template_name, {'form':form})

        context = {
            'form':form
        }

        messages.error(request, form.errors.as_text())
        return render(request, self.template_name, context)

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
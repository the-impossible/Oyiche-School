from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# My app imports
from oyiche_schMGT.models import *
from oyiche_auth.forms import *
from oyiche_schMGT.forms import *

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

class UpdateProfileView(LoginRequiredMixin, View):

    template_name = "backend/auth/update_profile.html"

    form = ProfleEditForm

    # Context variables
    object = None
    context = {}

    def get(self, request):

        self.object = User.objects.filter(user_id=request.user.user_id).first()
        self.form = self.form(instance=self.object)
        self.context['form'] = self.form

        return render(request, template_name=self.template_name, context=self.context)

    def post(self, request):

        self.object = User.objects.filter(user_id=request.user.user_id).first()

        if 'update_profile' in request.POST:

            form = self.form(instance=self.object, data=request.POST, files=request.FILES)

            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully')
                return redirect('auth:update_profile')
            else:
                self.context['form'] = form
                messages.error(request, form.errors.as_text())

        elif 'update_password' in request.POST:

            old_password = request.POST.get('old_password')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            self.form = self.form(instance=self.object)

            self.context = {
                'old_password': old_password,
                'password': password,
                'confirm_password': confirm_password,
                'form': self.form,
            }

            route = render(request, template_name=self.template_name, context=self.context)

            if (password != confirm_password):
                messages.error(
                    request, 'New password and confirm password does not match!')
                return route

            if (len(confirm_password) < 6):
                messages.error(
                    request, 'password too short! should not be less than 6 characters')
                return route

            if not self.object.check_password(old_password):
                messages.error(request, 'Old password incorrect!')
                return route

            self.object.set_password(password)
            self.object.save()

            messages.success(
                request, 'Password reset successful, you can now login!!')
            return redirect('auth:login')

        return render(request, template_name=self.template_name, context=self.context)

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import *
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

# My app imports
from oyiche_schMGT.models import *
from oyiche_auth.forms import *
from oyiche_schMGT.forms import *
from oyiche_schMGT.views import get_school
from oyiche_auth.decorators import *

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

        if self.object.userType.user_title.lower() == 'student':
            student = StudentInformation.objects.filter(user=self.object).first()
            self.context['student'] = student

        if self.object.userType.user_title.lower() == 'admin':
            admin = SchoolAdminInformation.objects.filter(user=self.object).first()
            self.context['admin'] = admin

        self.form = self.form(instance=self.object)
        self.context['form'] = self.form


        return render(request, template_name=self.template_name, context=self.context)

    def post(self, request):

        self.object = User.objects.filter(user_id=request.user.user_id).first()

        if self.object.userType.user_title.lower() == 'student':
            student = StudentInformation.objects.filter(user=self.object).first()
            self.context['student'] = student

        if self.object.userType.user_title.lower() == 'admin':
            admin = SchoolAdminInformation.objects.filter(user=self.object).first()
            self.context['admin'] = admin

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

@method_decorator([is_school], name='dispatch')
class AdminRegistrationView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = SchoolAdminInformation
    form_class = AdminForm
    template_name = "backend/auth/admin.html"
    success_message = "Admin Account created!"

    def get_success_url(self):
        return reverse("auth:manage_admin")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = SchoolAdminInformation.objects.filter(
            school=get_school(self.request))
        return context

    def form_valid(self, form):
        userType = UserType.objects.get_or_create(user_title='admin')[0]
        form.instance.userType = userType

        try:
            school = get_school(self.request)
            admin_name = form.cleaned_data.get('admin_name')
            gender = form.cleaned_data.get('gender')

            response = super().form_valid(form)

            SchoolAdminInformation.objects.create(
                user=self.object, school=school, admin_name=admin_name, gender=gender)

            return response

        except Exception as e:

            messages.error(
                self.request, f"FAILED: {e}!!")
            return self.render_to_response(self.get_context_data(form=form))

@method_decorator([is_school], name='dispatch')
class DeleteAdminView(LoginRequiredMixin,SuccessMessageMixin, DeleteView):
    model = User
    success_message = "Admin account has been deleted successfully!"

    def get_success_url(self):
        return reverse("auth:manage_admin")

@method_decorator([is_school], name='dispatch')
class AdminEditView(LoginRequiredMixin, View):

    def get(self, request, pk):
        school = get_school(request)

        try:
            admin_info = SchoolAdminInformation.objects.get(school=school, pk=pk)
            admin_user_info = User.objects.get(user_id=admin_info.user_id)
            admin_form = AdminEditForm(instance=admin_user_info, initial={'password':'', 'gender':admin_info.gender, 'admin_name':admin_info.admin_name}, school=school)

            return render(request=request, template_name="backend/auth/partials/admin_form.html", context={'form': admin_form, 'object': admin_info})

        except SchoolAdminInformation.DoesNotExist:
            return JsonResponse({'error': 'Admin not found!'}, status=404)

    def post(self, request, pk):

        school = get_school(request=request) #Get school info

        try:

            admin_info = SchoolAdminInformation.objects.get(school=school, pk=pk)
            admin_user_info = User.objects.get(user_id=admin_info.user_id)

            form = AdminEditForm(request.POST, instance=admin_user_info, school=school)

            if form.is_valid():
                print("form is valid")
                data = form.save(commit=False)

                admin_name = form.cleaned_data.get('admin_name')
                gender = form.cleaned_data.get('gender')

                admin_updated_info = SchoolAdminInformation.objects.filter(pk=pk).update(
                    admin_name=admin_name,
                    gender=gender,
                )

                data.save()

                username = form.cleaned_data.get('username')
                messages.success(request, f"Admin: {username} successfully edited!!")

            else:
                print("form is invalid")
                print(form.errors.as_text())
                # If form is invalid, re-render the page with errors message
                messages.error(request, form.errors.as_text())

        except (SchoolAdminInformation, User).DoesNotExist:
            print("Admin not found")
            messages.error(request, "Failed to edit admin!!")

        finally:
            return HttpResponse('<script>window.location.reload();</script>')


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
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from Mail.utils import AppTokenGenerator
from django.forms import ValidationError

# My app imports
from Mail.emails.reset_password import ResetPassword
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
                school_info = SchoolInformation.objects.create(
                    principal_id=data,
                    school_email=email
                )

                all_terms = GeneralAcademicTerm.objects.all()
                academic_term_list = []

                for term in all_terms:
                    academic_term = AcademicTerm(
                        school_info=school_info,
                        term=term.term,
                        term_description=term.term_description,
                        is_current=term.is_current
                    )

                    academic_term_list.append(academic_term)

                AcademicTerm.objects.bulk_create(academic_term_list)

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

class ForgotPasswordView(View):
    """Handles user password reset email requests."""
    template_name = "backend/auth/forgot-password.html"

    def get(self, request):
        """Display Forgot Password page"""
        return render(request, self.template_name)

    def post(self, request):
        """Validate email and send reset password link."""
        email = request.POST.get('email', '').strip().lower()

        if not email:
            messages.error(request, "Please enter your email address!")
            return render(request, self.template_name)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.success(
                request,
                "If an account with that email exists, a password reset link has been sent."
            )
            return redirect('auth:forgot-password')

        # Send Forgot password email
        ResetPassword(request).send(
            user=user,
        )
        messages.success(request, 'If an account with that email exists, a password reset link has been sent.')
        return redirect('auth:forgot-password')

class ResetPasswordView(View):
    """Displays the reset password form after verifying token validity."""

    template_name = "backend/auth/reset_password.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.token_generator = AppTokenGenerator()

    def get(self, request, uidb64, token):
        """Verify reset link and show password reset form."""

        try:
            # Get uidb64
            uid = force_str(force_bytes(urlsafe_base64_decode(uidb64)))
            user = User.objects.get(user_id=uid)

        except (User.DoesNotExist, ValueError, OverflowError, TypeError):
            user = None

        if user is not None and self.token_generator.check_token(user, token):
            # Token is Valid
            context = {'uidb64':uidb64, 'token':token}
            messages.info(request, 'Create a new password for your account!')
            return render(request, self.template_name, context)
        else:
            # Invalid or Expired Link
            messages.info(request, 'Link broken or Invalid reset link, Please Request a new one!')
            return redirect('auth:forgot-password')

    def post(self, request, uidb64, token):
        """Change the User Password"""

        try:
            # Decode uid from URL
            uid = force_str(force_bytes(urlsafe_base64_decode(uidb64)).decode())
            user = User.objects.get(user_id=uid)

        except (User.DoesNotExist, ValueError, OverflowError, TypeError):
            user = None

        if not user:
            messages.error(request, 'Oops user does not exist!')
            return redirect('auth:forgot-password')

        password1 = request.POST['password']
        password2 = request.POST['confirmPassword']

        context = {'uidb64':uidb64, 'token':token}

        try:
            self.validate_password(password1=password1, password2=password2)
        except ValidationError as e:
            messages.error(request, e.message)
            return render(request, self.template_name, context)

        user.set_password(password1)
        user.save()
        messages.success(request, 'Password changed successfully! You can now log in with your new password.')
        return redirect('auth:login')

    def validate_password(self, password1, password2):
        """Validate password strength and match"""

        if(password1 != password2):
            raise ValidationError("Passwords do not match!")

        pattern = re.compile(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()[\]{}<>~_+=|:;.,-]).{8,}$'
        )

        if not pattern.match(password1):
            raise ValidationError(
                "Password must be at least 8 characters long, and include uppercase, lowercase, number, and special character."
            )

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
                # If form is invalid, re-render the page with errors message
                messages.error(request, form.errors.as_text())

        except (SchoolAdminInformation, User).DoesNotExist:
            messages.error(request, "Failed to edit admin!!")

        finally:
            return HttpResponse('<script>window.location.reload();</script>')


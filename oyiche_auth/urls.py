# My Django imports
from django.urls import path, include

app_name = 'auth'

# My App imports
from oyiche_auth.views import *

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('forgot-password', ForgotPasswordView.as_view(), name="forgot-password"),

    path('dashboard', DashboardView.as_view(), name="dashboard"),
    path("update_profile", UpdateProfileView.as_view(), name="update_profile"),
    path("manage_admin", AdminRegistrationView.as_view(), name="manage_admin"),
    path("delete_admin/<str:pk>", DeleteAdminView.as_view(), name="delete_admin"),

]

handler404 = "oyiche_auth.views.custom_404_view"
# My Django imports
from django.urls import path, include

app_name = 'basic'

# My App imports
from oyiche_basic.views import *

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('about', AboutView.as_view(), name="about"),
    path('contact', ContactView.as_view(), name="contact"),
    path('blog', BlogView.as_view(), name="blog"),
    path('privacy-policy', PrivacyPolicyView.as_view(), name="privacy-policy"),
]

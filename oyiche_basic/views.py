# My Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse

# My App imports
from oyiche_basic.models import *
from oyiche_basic.forms import *

# Create your views here.

class HomeView(TemplateView):
    template_name = "frontend/home.html"

class AboutView(TemplateView):
    template_name = "frontend/about.html"

class ContactView(SuccessMessageMixin, CreateView):
    template_name = "frontend/contact.html"
    model = ContactUs
    form_class = ContactUsForm
    success_message = "We have received your message, we will get in touch shortly!"

    def get_success_url(self):
        return reverse("basic:contact")

class BlogView(TemplateView):
    template_name = "frontend/blog.html"


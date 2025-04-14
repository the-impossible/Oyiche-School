# My Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import HttpResponse, JsonResponse
import pandas as pd
from urllib.parse import urlencode
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.db.models import Q

# My App imports
from oyiche_schMGT.models import *
from oyiche_schMGT.forms import *
from oyiche_files.forms import *
from oyiche_files.models import *
from oyiche_schMGT.utils import *
from oyiche_auth.decorators import *
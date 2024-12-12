# My django imports
from django.contrib import admin

# My App Imports
from oyiche_auth.models import *
# Register your models here.
admin.site.register(UserType)
admin.site.register(User)

# My django imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# My App Imports
from oyiche_auth.models import *

# Register your models here.
class UserAdmin(UserAdmin):
    list_display = ('username', 'userType', 'email', 'phone', 'pic', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username','phone','email',)
    ordering = ('username',)
    readonly_fields = ('date_joined', 'last_login',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(UserType)
admin.site.register(User, UserAdmin)

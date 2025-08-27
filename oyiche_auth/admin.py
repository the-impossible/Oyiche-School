# # My django imports
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin

# # My App Imports
# from oyiche_auth.models import *

# # Register your models here.

# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     model = User
#     autocomplete_fields = ('userType',)
#     list_display = ('username', 'userType', 'email', 'phone', 'pic', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser')
#     list_editable = ('userType', 'email', 'phone', 'pic', 'is_active', 'is_staff', 'is_superuser')
#     list_filter = ('userType', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
#     search_fields = ('username','phone','email',)
#     list_per_page = 100

#     ordering = ('-date_joined',)
#     readonly_fields = ('date_joined', 'last_login')

# @admin.register(UserType)
# class UserTypeAdmin(admin.ModelAdmin):
#     list_display = ('user_type_id', 'user_title', 'user_description')
#     list_editable = ('user_title', 'user_description')
#     search_fields = ('user_title',)
#     list_per_page = 10

#     ordering = ('user_title',)

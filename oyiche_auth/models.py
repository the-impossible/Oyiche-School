# My Django imports
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import uuid
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseNotFound
from django.template.loader import render_to_string

# My app imports
from oyiche_schMGT.models import *

# Create your models here.


class UserType(models.Model):
    user_title = models.CharField(max_length=20, unique=True)
    user_description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user_title

    class Meta:
        db_table = 'UserType'
        verbose_name_plural = 'UserType'


class UserManager(BaseUserManager):
    def create_user(self, schId, userType, password=None):

        # creates a user with the parameters
        if not schId:
            raise ValueError('School ID is required!')

        if not userType:
            raise ValueError('userType is required!')

        if password is None:
            raise ValueError('Password is required!')

        user = self.model(
            username=schId.upper().strip(),
            userType=userType,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None):
        # create a superuser with the above parameters
        if not username:
            raise ValueError('Username is required!')

        userType = UserType.objects.get_or_create(user_title='admin')[0]

        if password is None:
            raise ValueError('Password should not be empty')

        user = self.create_user(
            schId=username.upper().strip(),
            userType=userType,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    user_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    username = models.CharField(
        max_length=20, db_index=True, unique=True, blank=True)
    userType = models.ForeignKey(
        to="UserType", on_delete=models.CASCADE, blank=True, null=True)

    phone = models.CharField(max_length=11, db_index=True,
                             unique=True, blank=True, null=True)
    pic = models.ImageField(default='img/user.png',
                            null=True, blank=True, upload_to='uploads/profile/')
    email = models.CharField(max_length=100, db_index=True, unique=True,
                             verbose_name='email address', blank=True, null=True)

    date_joined = models.DateTimeField(
        verbose_name='date_joined', auto_now_add=True)
    last_login = models.DateTimeField(
        verbose_name='last_login', auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.username.upper()}'

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True

    def get_school_name(self):
        try:
            if str(self.userType) == 'school':
                # Fetching SchoolInformation by principal_id
                school = SchoolInformation.objects.get(principal_id=self.user_id)
                return school.school_username

            elif str(self.userType) == 'student':
                # Fetching StudentInformation and related school
                student = StudentInformation.objects.get(user_id=self.user_id)
                return student.school.school_username

            elif str(self.userType) == 'admin':
                return 'Oyiche'

            # If userType does not match any expected value
            return None

        except SchoolInformation.DoesNotExist:
            # Redirecting to 404 page if SchoolInformation not found
            raise Http404("School Information not Found! contact Host.")

        except StudentInformation.DoesNotExist:
            # Redirecting to 404 page if StudentInformation not found
            raise Http404("School Information not Found! contact School.")

        except Exception as e:
            # Handling any other exception and redirecting to login page
            return redirect('auth:login')  # Redirect to login page in case of unexpected errors

    class Meta:
        db_table = 'Users'
        verbose_name_plural = 'Users'

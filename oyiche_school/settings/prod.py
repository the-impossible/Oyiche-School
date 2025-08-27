from .base import *

# # Database
# # https://docs.djangoproject.com/en/5.1/ref/settings/#databases

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

# ALLOWED_HOSTS = ['school.oyichetech.com', 'www.school.oyichetech.com']
ALLOWED_HOSTS = ['oyicheacademy.com', 'www.oyicheacademy.com']

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': 3306,
    }
}

STATIC_ROOT = '/home/ocukczjrol/oyicheacademy.com/static'
MEDIA_ROOT = '/home/ocukczjrol/oyicheacademy.com/media'

HTTP = 'https://'

# STATIC_ROOT = '/home/ocukczjrol/school.oyichetech.com/static'
# MEDIA_ROOT = '/home/ocukczjrol/school.oyichetech.com/media'
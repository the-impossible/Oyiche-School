from .base import *
from decouple import config

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': 'postgres',
        'PASSWORD': 'impossible081',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'Static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

HTTP = 'http://'
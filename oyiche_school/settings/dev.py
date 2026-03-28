from .base import *
from decouple import config

# INSTALLED_APPS += [
#     'debug_toolbar',
# ]

# MIDDLEWARE += [
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# ]

# INTERNAL_IPS = [
#     # ...
#     "127.0.0.1",
#     # ...
# ]

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "oyiche_academy",
        # 'USER': "the-impossible",
        'USER': "root",
        'PASSWORD': "@Rich@rich1",
        'HOST': 'localhost',
        'PORT': 3306,
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': config('DB_NAME'),
#         'USER': 'root',
#         'PASSWORD': '@Eghe@eghe1',
#         'HOST': 'localhost',
#         'PORT': 3306,
#     }
# }

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'Static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

HTTP = 'http://'
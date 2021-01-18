from decouple import config, Csv
import dj_database_url
from jumga.settings.common import *

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': dj_database_url.config(
#         default=config('DATABASE_URL')
#     )
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.abspath(os.path.dirname(__name__)) + '/db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', cast=Csv(post_process=tuple))

PROJECT_ACCESS_KEY = config('PROJECT_ACCESS_KEY').encode()

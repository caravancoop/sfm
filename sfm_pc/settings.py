"""
Django settings for sfm_pc project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket

import dj_database_url
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.contrib.messages import constants as messages


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
    IMPORTER_USER_PASSWORD = os.environ['IMPORTER_USER_PASSWORD']
except KeyError:
    raise Exception('DJANGO_SECRET_KEY and IMPORTER_USER_PASSWORD must be declared as environment variables')

DEBUG = False if os.getenv('DJANGO_DEBUG', 'True') == 'False' else True
ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',') if os.getenv('ALLOWED_HOSTS', None) else []
DATABASE_URL = os.getenv('DATABASE_URL', 'postgis://postgres:postgres@postgres:5432/sfm')
SOLR_URL = os.getenv('SOLR_URL', 'http://solr:8983/solr/sfm')

GOOGLE_MAPS_KEY = os.getenv('GOOGLE_MAPS_KEY', '')
SENTRY_DSN = os.getenv('SENTRY_DSN', '')

# Application definition

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.humanize',
    'haystack',
    'django_date_extensions',
    'rosetta',
    'languages_plus',
    'countries_plus',
    'reversion',
    'leaflet',
    'bootstrap_pagination',
    'complex_fields',
    'sfm_pc',
    'organization',
    'person',
    'personbiography',
    'personextra',
    'membershiporganization',
    'membershipperson',
    'composition',
    'source',
    'area',
    'association',
    'geosite',
    'emplacement',
    'violation',
    'location',
    'search',
    'raven.contrib.django.raven_compat',
    'debug_toolbar',
)

if SENTRY_DSN:
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'sfm_pc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sfm_pc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# Parse database configuration from $DATABASE_URL
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

FIXTURES_DIRS = (
    BASE_DIR + "/fixtures",
)

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGES = (
    ('fr', _('French')),
    ('en', _('English')),
    ('es', _('Spanish')),
    ('ar', _('Arabic'))
)

LOCALE_PATHS = (
    BASE_DIR + '/locale',
)

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_EXTENSIONS_OUTPUT_FORMAT_DAY_MONTH_YEAR = "j F Y"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = reverse_lazy('login')

AUTHENTICATION_BACKENDS = (
    'sfm_pc.backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Caching

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'sfm_cache',
        }
    }

# Search

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': SOLR_URL,
        'SILENTLY_FAIL': False,
        'BATCH_SIZE': 5,
        'INCLUDE_SPELLING': True,
    },
}

HAYSTACK_DOCUMENT_FIELD = 'content'

# Update index on model change
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Miscellaneous

IMPORTER_USER = {
    'username': 'importer',
    'password': IMPORTER_USER_PASSWORD,
    'email': 'importer@importer.com',
    'first_name': 'Imp',
    'last_name': 'Orter',
    'is_staff': False,
}

SITE_ID = 1

ALLOWED_CLASS_FOR_NAME = [
    'Person', 'Organization', 'MembershipPerson', 'Composition', 'Association', 'Area',
    'Emplacement', 'Geosite', 'Violation', 'MembershipOrganization',
    'PersonExtra', 'PersonBiography'
]

# Override built-in messages tags
MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success'
}

CONFIDENCE_LEVELS = (
    ('1', _('Low')),
    ('2', _('Medium')),
    ('3', _('High')),
)

OPEN_ENDED_CHOICES = (
    ('Y', _('Yes')),
    ('N', _('No')),
    ('E', _('Exact'))
)

# Format this string with the user's language code
RESEARCH_HANDBOOK_URL = "https://help.securityforcemonitor.org"

# Disable Django Debug Toolbar unless a specific env var is set. See:
# https://coderwall.com/p/-tikrw/disable-django-debug-toolbar-when-debug-true
if os.getenv('DJANGO_DEBUG_TOOLBAR', False):
    *_, ips = socket.gethostbyname_ex(socket.gethostname())

    INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1']

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
else:
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda x: False  # Disable it
    }

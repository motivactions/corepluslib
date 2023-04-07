import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR / "example"

SECRET_KEY = "django-insecure-66#za9zotp07tf*mfeifb-vfu_x+y&b#v==oh58c#6vzn3)c*s"

SITE_ID = 1
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "example.app",
    "coreplus.docs",
    "coreplus.api",
    "coreplus.numerators",
    "coreplus.navigators",
    "coreplus.markdown",
    "coreplus.contacts",
    "coreplus.settings",
    "coreplus",
    # Dependencies
    "easy_thumbnails",
    "rest_framework",
    #
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "example.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DJANGO_VALIDATIONS = "django.contrib.auth.password_validation"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": DJANGO_VALIDATIONS + ".UserAttributeSimilarityValidator"},
    {"NAME": DJANGO_VALIDATIONS + ".MinimumLengthValidator"},
    {"NAME": DJANGO_VALIDATIONS + ".CommonPasswordValidator"},
    {"NAME": DJANGO_VALIDATIONS + ".NumericPasswordValidator"},
]

TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("id", "Indonesia"),
    ("en", "English (United States)"),
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [os.path.join(PROJECT_DIR, "static")]
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")
MEDIA_URL = "/media/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


##############################################################################
# Search Engine Settings
##############################################################################

SEARCH_ENGINE = os.getenv("SEARCH_ENGINE", "whoosh")
HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": os.path.join(BASE_DIR, "whoosh"),
        "STORAGE": "file",
        "POST_LIMIT": 128 * 1024 * 1024,
        "INCLUDE_SPELLING": True,
        "BATCH_SIZE": 100,
        "EXCLUDED_INDEXES": ["thirdpartyapp.search_indexes.BarIndex"],
    },
}

if SEARCH_ENGINE == "elastic_search":
    HAYSTACK_CONNECTIONS = {
        "default": {
            "ENGINE": "haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine",  # NOQA
            "INDEX_NAME": os.getenv("SEARCH_INDEX_NAME"),
            "TIMEOUT": 60 * 5,
            "INCLUDE_SPELLING": True,
            "BATCH_SIZE": 100,
        }
    }
elif SEARCH_ENGINE == "algolia":
    INSTALLED_APPS.append("algoliasearch_django")
    ALGOLIA = {
        "APPLICATION_ID": os.getenv("ALGOLIA_APP_ID"),
        "API_KEY": os.getenv("ALGOLIA_API_KEY"),
        "INDEX_PREFIX": os.getenv("SEARCH_INDEX_NAME"),
        "AUTO_INDEXING": True,
        "RAISE_EXCEPTIONS": os.getenv("DEBUG"),
    }

##############################################################################
# PUSH Notification Settings
##############################################################################

WEB_PUSH_SERVER_KEY = ""  # NOQA

PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": "AAAA3B09Grs:APA91bFn-x6a7wdioD6S8Ohn4gVVs8gHBXBExHpxzHWVZu85Su-u8gaElRugyXwcgRgigxQveZVOoAqGGyyZi270xZih2YAjVCjuFM0BIrZsG1Sjo_PnneRnqxTvIEnp20DjhhTdKDM5",  # NOQA
    "FCM_POST_URL": "https://fcm.googleapis.com/fcm/send",  # (optional)
    "FCM_MAX_RECIPIENTS": 1000,
    # "APNS_CERTIFICATE": "/path/to/your/certificate.pem",
    # "APNS_TOPIC": "com.example.push_test",
    # "WP_PRIVATE_KEY": os.path.join(BASE_DIR, "private_key.pem"),
    # "WP_CLAIMS": {"sub": "mailto: sasri.project@gmail.com"},
    # "WP_POST_URL": "" (optional)
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

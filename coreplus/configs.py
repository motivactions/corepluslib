"""
    This module is largely inspired by django-rest-framework settings.
    This module provides the `settings` object, that is used to access
    app settings, checking for user settings first, then falling
    back to the defaults.
"""
import os
from typing import Any, Dict

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

SETTINGS_DOC = "https://gitlab.com/zeroplus/django/django-coreplus/-/wikis/"

COREPLUS_DEFAULTS: Dict[str, Any] = {
    # Examples
    # ------------------------------------------------------------------------
    # "SETTING_NAME": getattr(settings, "SETTING_NAME", "default_value"),
    # "SETTING_MODULE_FROM_STRING": getattr(
    #     settings, "SETTING_MODULE_FROM_STRING", "your.module.name"
    # ),
    # "SETTING_MODULE_FROM_LIST_STRING": getattr(
    #     settings, "SETTING_MODULE_FROM_LIST_STRING", [
    #                   "your.module.name1",
    #                   "your.module.name2"
    #     ]
    # ),
    # "SETTING_MODULE_FROM_DICT_STRING": {
    #     "some_key1": "some.module.name1",
    #     "some_key2": "some.module.name2",
    # },
    #
    "HOOK_FILE_NAME": "corehooks",
    "REQUIRED_ADDRESS_FIELDS": [],

    # API Settings
    # ===================================================================
    "DEFAULT_USER_SERIALIZER": "coreplus.api.endpoints.serializers.CorePlusUserSerializer",

    # Admin Settings
    # ===================================================================
    "APP_INDEX_EXCLUDES": [],
    "INDEX_TITLE": os.getenv("INDEX_TITLE", "Platform Administration"),
    "SITE_TITLE": os.getenv("SITE_TITLE", "Platform Administration"),
    "SITE_HEADER": os.getenv("SITE_HEADER", "Platform Administration"),
    "LOGOUT_TEMPLATE": "registration/logged_out.html",
    "APP_INDEX_TEMPLATE": "admin/app_index.html",
    "DEFAULT_APP_ICONS": {
        "taggit": "tag-outline",
        "sites": "web",
        "account": "at",
        "socialaccount": "webhook",
        "auth": "account-circle-outline",
        "django_numerator": "barcode",
        "filer": "folder-open-outline",
        "cms": "book-open-outline",
    },
    "PRINT_OPTIONS": {
        "page_size": "A4",
        "background": True,
        "margin_top": 20,
        "margin_bottom": 20,
        "margin_left": 20,
        "margin_right": 20,
        "orientation": "portrait",
        "disable_smart_shrinking": True,
        "zoom": 0.5,
    },
    "PRINT_VIEW_CLASS": "coreplus.admin.mixins.PDFPrintView",
    # Media Settings
    # ===================================================================
    "IMAGE_FILE_EXTENSIONS": [
        ".jpg",
        ".jpeg",
        ".png",
        ".svg",
        ".webp",
        ".jfif",
        ".pjpeg",
        ".pjp",
    ],
    "AUDIO_FILE_EXTENSIONS": [".mp3", ".aac", ".wav", ".aiff", ".ogg"],
    "VIDEO_FILE_EXTENSIONS": [
        ".gif",
        ".mp4",
        ".mov",
        ".wmv",
        ".avi",
        ".avchd",
        ".html5",
        ".webm",
        ".mkv",
        ".flv",
    ],
    "DOCUMENT_FILE_EXTENSIONS": [
        ".doc",
        ".docx",
        ".docm",
        ".html",
        ".pdf",
        ".txt",
        ".xml",
        ".csv",
        ".xls",
        ".xlsb",
        ".xlsm",
        ".xlsx",
        ".xlt",
        ".pot",
        ".potx",
        ".potm",
        ".ppt",
        ".pptm",
        ".pptx",
        ".xps",
    ],
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = [
    "PRINT_VIEW_CLASS", "DEFAULT_USER_SERIALIZER",
]

# List of settings that have been removed
REMOVED_SETTINGS = []


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    elif isinstance(val, dict):
        return {
            key: import_from_string(item, setting_name) for key, item in val.items()
        }
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for COREPLUS setting '%s'. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class AppSettings:
    """
    This module is largely inspired by django-rest-framework settings.
    This module provides the `coreplus_settings` object, that is used to access
    app settings, checking for user settings first, then falling
    back to the defaults.
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or COREPLUS_DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "COREPLUS", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid COREPLUS settings: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    "The '%s' setting has been removed. Please refer to '%s' "
                    "for available settings." % (setting, SETTINGS_DOC)
                )
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


coreplus_configs = AppSettings(None, COREPLUS_DEFAULTS, IMPORT_STRINGS)


def reload_coreplus_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "COREPLUS":
        coreplus_configs.reload()


setting_changed.connect(reload_coreplus_settings)

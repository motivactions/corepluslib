from django.core.exceptions import ValidationError

from .extras import SpamFilter

sf = SpamFilter()


def validate_is_spam(value):
    if sf.is_spam(value):
        raise ValidationError("Content is considered as spam.")

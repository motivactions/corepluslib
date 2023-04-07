from .extras import SpamFilter

sf = SpamFilter()


def is_spam(value):
    return sf.is_spam(value)

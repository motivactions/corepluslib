import re
from decimal import Decimal as D
from decimal import InvalidOperation

from babel.numbers import format_currency
from django.conf import settings
from django.utils.formats import number_format
from django.utils.translation import get_language, to_locale

CURRENCY_DEFAULT = "IDR"
CURRENCY_FORMAT_DEFAULT = {
    "USD": {
        "currency_digits": False,
        "format_type": "accounting",
    },
    "IDR": {
        "format": "\xa0¤ #,##0",
        "locale": "id_id",
        "currency_digits": True,
        "format_type": "standart",
    },
}

CURRENCY = getattr(settings, "CURRENCY", CURRENCY_DEFAULT)
CURRENCY_FORMAT = getattr(settings, "CURRENCY_FORMAT", CURRENCY_FORMAT_DEFAULT)


def currency(value, currency=None):
    """
    Format decimal value as currency
    """
    if currency is None:
        currency = CURRENCY
    try:
        value = D(value)
    except (TypeError, InvalidOperation):
        return ""
    # Using Babel's currency formatting
    # http://babel.pocoo.org/en/latest/api/numbers.html#babel.numbers.format_currency
    kwargs = {
        "currency": currency,
        "locale": to_locale(get_language() or settings.LANGUAGE_CODE),
    }
    if isinstance(CURRENCY_FORMAT, dict):
        kwargs.update(CURRENCY_FORMAT.get(currency, {}))
    else:
        kwargs["format"] = CURRENCY_FORMAT
    return format_currency(value, **kwargs).strip()


def money(value, use_l10n=True):
    """
    Convert an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    if value is None:
        return money(0, use_l10n)
    if settings.USE_L10N and use_l10n:
        try:
            if not isinstance(value, (float, D)):
                value = int(value)
        except (TypeError, ValueError):
            return money(value, False)
        else:
            return number_format(value, decimal_pos=2, force_grouping=True)
    orig = str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1>,\g<2>", orig)
    if orig == new:
        return new
    else:
        return money(new, use_l10n)


def number_to_text_id(number):
    """
    Convert number to sentence (id)
    :param number: interger
    :return: string
    """
    words = [
        "",
        "satu",
        "dua",
        "tiga",
        "empat",
        "lima",
        "enam",
        "tujuh",
        "delapan",
        "sembilan",
        "sepuluh",
        "sebelas",
    ]
    if number < 0:
        number = 0
    number = int(number)
    if number == 0:
        return ""
    elif number < 12 and number != 0:
        return "" + words[number]
    elif number < 20:
        return number_to_text_id(number - 10) + " belas "
    elif number < 100:
        return (
            number_to_text_id(number / 10) + " puluh " + number_to_text_id(number % 10)
        )
    elif number < 200:
        return "seratus " + number_to_text_id(number - 100)
    elif number < 1000:
        return (
            number_to_text_id(number / 100)
            + " ratus "
            + number_to_text_id(number % 100)
        )
    elif number < 2000:
        return "seribu " + number_to_text_id(number - 1000)
    elif number < 1000000:
        return (
            number_to_text_id(number / 1000)
            + " ribu "
            + number_to_text_id(number % 1000)
        )
    elif number < 1000000000:
        return (
            number_to_text_id(number / 1000000)
            + " juta "
            + number_to_text_id(number % 1000000)
        )
    elif number < 1000000000000:
        return (
            number_to_text_id(number / 1000000000)
            + " milyar "
            + number_to_text_id(number % 1000000000)
        )
    elif number < 100000000000000:
        return (
            number_to_text_id(number / 1000000000000)
            + " trilyun "
            + number_to_text_id(number % 1000000000000)
        )
    elif number <= 100000000000000:
        return "Jumlah terlalu besar!"

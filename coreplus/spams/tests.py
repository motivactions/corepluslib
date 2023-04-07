from django.test import TestCase, tag

from .extras import SpamFilter
from .validators import validate_is_spam


class SpamTestCase(TestCase):
    def setUp(self) -> None:
        self.spam = SpamFilter()
        return super().setUp()

    @tag("spam_test")
    def test_english_spam_filter(self):
        res = self.spam.is_spam(
            "Please like and share our product at https://www.google.com"
        )
        self.assertEqual(res, True)
        res = self.spam.is_spam("isnt just possible now")
        self.assertEqual(res, False)

    @tag("spam_test")
    def test_indo_spam_filter(self):
        res = self.spam.is_spam("bagikan dan sukai produk dari https://www.google.com")
        self.assertEqual(res, True)
        res = self.spam.is_spam("Paket tadi sore mendadak habis.")
        self.assertEqual(res, False)

    @tag("spam_test")
    def test_english_spam_validate(self):
        validate_is_spam("isnt just possible now")

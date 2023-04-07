from django.test import TestCase, tag

from .extras import ProfanityFilter


class ProfanityTestCase(TestCase):
    def setUp(self) -> None:
        self.profanity = ProfanityFilter()
        return super().setUp()

    @tag("profanity_test")
    def test_profanity_filter_in_text(self):
        cencored = self.profanity.censor("iih, fucker boy")
        self.assertEqual(cencored, "iih, ****** boy")

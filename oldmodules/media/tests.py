from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import TestCase, tag

from .helpers import validate_file_type_api

User = get_user_model


class MediaTest(TestCase):
    @tag("media_unit_test")
    def test_validate_file_type(self):
        img = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        img.name = "image.png"
        validate_file_type_api(img, [".png"])

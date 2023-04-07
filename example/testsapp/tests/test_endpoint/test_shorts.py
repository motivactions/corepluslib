from django.contrib.auth import get_user_model
from django.test import tag

from rest_framework.test import APILiveServerTestCase

shortened_urls = ""


class ShortnersUrlTest(APILiveServerTestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test",
            email="test@mail.com",
            password="testpassword",
        )
        self.user.save()
        return super().setUp()

    @tag("shorts_test", "shorts_api_v1_endpoint")
    def test_create_shorten_url(self):
        payload = {
            "title": "testing title",
            "description": "testing description",
            "url_original": "https://www.google.com/",
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/v1/shorts/shorturl/", data=payload)
        self.assertEqual(response.status_code, 201)

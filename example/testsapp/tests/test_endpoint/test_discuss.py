from django.contrib.auth import get_user_model
from django.test import tag

from rest_framework.test import APILiveServerTestCase

from coreplus.discuss.models import Discuss


class DiscussApiTest(APILiveServerTestCase):
    BASE_URL = "/api/v1/discuss"

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test",
            email="test@yopmail.com",
            password="testpassword",
        )
        self.user.save()
        self.discuss = Discuss(user=self.user, content="test discuss")
        self.discuss.save()
        self.child = Discuss(
            user=self.user,
            content="child discuss",
            parent=self.discuss,
        )
        self.child.save()

    @tag("discuss_api_v1_endpoint")
    def test_discuss_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.BASE_URL}/discuss/")
        from pprint import pprint

        pprint(response.json())
        self.assertEqual(response.status_code, 200)

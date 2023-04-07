from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import tag

from rest_framework.test import APILiveServerTestCase

User = get_user_model


class MediaApiTest(APILiveServerTestCase):
    BASE_URL = "/api/v1/media"

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test",
            email="test@yopmail.com",
            password="testpassword",
        )
        self.user.save()
        return super().setUp()

    @tag("media_api_v1_endpoint")
    def test_file_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.BASE_URL}/file/")
        self.assertEqual(response.status_code, 200)

    @tag("media_api_v1_endpoint")
    def test_create_file(self):
        img = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        data = {"file": img}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"{self.BASE_URL}/file/", data)
        self.assertEqual(response.status_code, 201)

    @tag("media_api_v1_endpoint")
    def test_create_audio_visual(self):
        sound = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        sound.name = "sound.mp3"
        data = {"file": sound}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"{self.BASE_URL}/audio-visual/", data)
        self.assertEqual(response.status_code, 201)

    @tag("media_api_v1_endpoint")
    def test_create_single_image(self):
        img = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        img.name = "image.png"
        data = {"file": img}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"{self.BASE_URL}/image/", data)
        self.assertContains(response, "image.png", status_code=201)

    @tag("media_api_v1_endpoint")
    def test_create_multiple_image(self):
        img1 = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        img1.name = "image1.png"
        img2 = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        img2.name = "image2.png"
        data = {"file": [img1, img2]}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"{self.BASE_URL}/image/", data)
        self.assertContains(response, "image1.png", status_code=201)
        self.assertContains(response, "image2.png", status_code=201)

    # +++++++++++++++++++++++++++++++++++++
    # Negative Testing
    # +++++++++++++++++++++++++++++++++++++
    @tag("media_api_v1_endpoint")
    def test_wrong_type_image(self):
        img = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        img.name = "image.py"
        data = {"file": img}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"{self.BASE_URL}/image/", data)
        self.assertEqual(response.status_code, 400)

    @tag("media_api_v1_endpoint")
    def test_wrong_type_audio_visual(self):
        sound = BytesIO(b"\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00")
        sound.name = "sound.py"
        data = {"file": sound}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"{self.BASE_URL}/audio-visual/", data)
        self.assertEqual(response.status_code, 400)

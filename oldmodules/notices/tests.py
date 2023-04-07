from django.test import TestCase

# from push_notifications.gcm import send_bulk_message


class TestSendNotification(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    # def test_send_firebase_notification(self):
    #     res = send_bulk_message(
    #         registration_ids=["4"], data={"title": "hello test"}, cloud_type="FCM"
    #     )
    #     return res

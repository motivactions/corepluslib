from django.contrib.auth import get_user_model
from django.test import tag

from rest_framework.test import APITestCase

from .models import DirectMessage


class HeraldsTest(APITestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.sender = User.objects.create_user(
            username="sender", email="sender@yopmail.com", password="senderpassword"
        )
        self.sender.save()
        self.recipient = User.objects.create_user(
            username="recipient",
            email="recipient@yopmail.com",
            password="recipientpassword",
        )
        self.recipient.save()
        return super().setUp()

    @tag("heralds_unit_test")
    def test_create_direct_message(self):
        direct_message = DirectMessage(
            sender=self.sender,
            recipient=self.recipient,
            content="this is a test direct message",
            status="unread",
        )
        direct_message.save()

        total_messages = DirectMessage.objects.all().count()
        messages = DirectMessage.objects.get(id=direct_message.id)

        self.assertEqual(total_messages, 1)
        self.assertEqual(messages.content, "this is a test direct message")

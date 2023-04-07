from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


def create_user(
    username, password, email, is_active=True, is_staff=False, is_superuser=False
):
    try:
        new_user = User.objects.get(username=username)
        print("%s has been created" % new_user)
    except User.DoesNotExist:
        new_user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
        print(" Create new user: '%s'" % new_user)
    new_user.save()


class Command(BaseCommand):
    help = "Init demo, staff and admin user account"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        create_user(
            "demo", "demo", "demo@email.com", is_staff=False, is_superuser=False
        )
        create_user(
            "staff", "staff", "staff@email.com", is_staff=True, is_superuser=False
        )
        create_user(
            "admin", "admin", "admin@email.com", is_staff=True, is_superuser=True
        )

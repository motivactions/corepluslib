import os
import subprocess

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Build Sphinx Documentation"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        subprocess.run(
            ["sphinx-build", "-b", "html", settings.DOCS_SOURCE, settings.DOCS_ROOT]
        )

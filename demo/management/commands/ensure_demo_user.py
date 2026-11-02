import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Creates a single, non-privileged login account for this demo site.

    Reads DEMO_USER_USERNAME/EMAIL/PASSWORD from the environment. Intended to
    run on every container start since sqlite doesn't persist across Cloud Run
    instances; a no-op if the account already exists in that instance's DB.
    """

    help = "Idempotently creates the demo site's non-superuser login account."

    def handle(self, *args, **options):
        username = os.environ.get('DEMO_USER_USERNAME')
        password = os.environ.get('DEMO_USER_PASSWORD')
        email = os.environ.get('DEMO_USER_EMAIL', '')

        if not username or not password:
            self.stdout.write('DEMO_USER_USERNAME/PASSWORD not set; skipping.')
            return

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"User '{username}' already exists; skipping.")
            return

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False,
        )
        self.stdout.write(f"Created non-privileged user '{username}'.")

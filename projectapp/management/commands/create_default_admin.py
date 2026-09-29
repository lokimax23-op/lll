import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or repair the default admin user for the project"

    def handle(self, *args, **options):
        admin_username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        admin_email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        admin_password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not all((admin_username, admin_email, admin_password)):
            self.stdout.write(
                self.style.WARNING(
                    "Admin account not created: set DJANGO_SUPERUSER_USERNAME, "
                    "DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": admin_email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if not created:
            user.email = admin_email
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["email", "is_staff", "is_superuser"])
            self.stdout.write(
                self.style.WARNING(f"Admin user '{admin_username}' already existed and was updated.")
            )
            return

        user.set_password(admin_password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f"Admin user '{admin_username}' created successfully.")
        )
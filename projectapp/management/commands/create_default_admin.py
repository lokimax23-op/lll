from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or repair the default admin user for the project"

    admin_username = "my_admin"
    admin_email = "example@gmail.com"
    admin_password = "my_admin_password"

    def handle(self, *args, **options):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=self.admin_username,
            defaults={
                "email": self.admin_email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if not created:
            user.email = self.admin_email
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["email", "is_staff", "is_superuser"])
            self.stdout.write(
                self.style.WARNING(f"Admin user '{self.admin_username}' already existed and was updated.")
            )
            return

        user.set_password(self.admin_password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f"Admin user '{self.admin_username}' created successfully.")
        )
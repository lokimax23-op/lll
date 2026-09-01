from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    admin_username = 'my_admin'
    admin_email = 'example@gmail.com'
    admin_password = 'my_admin_password'
    help = "help to create default admin user"
    
    
    def handle(self, *args, **kwargs):
        if not User.objects.filter(username=self.admin_username).exists():
           self.style.ERROR(f"Admin user '{self.admin_username}' already exists.")
           
        else:
           admin_user = User.objects.create_superuser(
                username=self.admin_username,
                email=self.admin_email,
                password=self.admin_password
            )
           
        self.stdout.write(
            self.style.SUCCESS(f"Admin user '{self.admin_username}' created successfully."    
            ))
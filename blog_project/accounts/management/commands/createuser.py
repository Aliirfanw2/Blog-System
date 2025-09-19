from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create a new user with specified username, email, and password'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the new user')
        parser.add_argument('email', type=str, help='Email for the new user')
        parser.add_argument('password', type=str, help='Password for the new user')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f"User with username '{username}' already exists."))
            return
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"User '{username}' created successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating user '{username}': {e}"))
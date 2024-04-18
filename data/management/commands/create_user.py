from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

UserModel = get_user_model


class Command(BaseCommand):
    """
    This command is designed to create a user with a specified email and
    password.
    If a user with the same email already exists, it will print a warning
    message.
    Otherwise, it will create the user and print a success message.
    """

    help = "This command creates a user."

    def handle(self, *args, **options):
        try:
            UserModel.objects.create_user("e@mail.com", "TestPassw0rd!")
        except IntegrityError:
            self.stdout.write(self.style.WARNING("Exists already!"))
        else:
            self.stdout.write(self.style.SUCCESS("User successfully created!"))

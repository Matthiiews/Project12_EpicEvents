import sys

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.core.management import call_command

from accounts.models import Employee

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table
from cli.utils_messages import create_error_message, create_success_message


userModel = get_user_model


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed to
    facilitate the creation of new employees within a system. It is
    specifically tailored for users with "MA" permissions, indicating that it
    is intended for management.
    """

    help = "Prompts to create a new employee."
    action = "CREATE"
    permissions = ["MA"]

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for employee in self.queryset:
            employee_data = {
                "email": employee.user.email,
                "name": employee.get_full_name,
                "role": employee.role,
            }
            table_data[f"Employee {employee.id}"] = employee_data

        create_queryset_table(
            table_data, "Employee", headers=self.headers["employee"])

    def get_data(self):
        self.display_input_title("Enter details to create an employee:")

        return {
            "email": self.email_input("Email address"),
            "password": self.password_input("Password"),
            "first_name": self.text_input("First name"),
            "last_name": self.text_input("Last name"),
            "role": self.choice_str_input(
                ("SA", "SU", "MA"), "Role [SA]les, [SU]pport, [MA]nagement")
        }

    @transaction.atomic
    def make_changes(self, data):
        try:
            user = userModel.objects.create_user(
                data.pop("email", None), data.pop("password", None))
            self.object = Employee.objects.create(**data, user=user)
            return self.object
        except IntegrityError:
            create_error_message("Email")
            call_command("employee_create")
            sys.exit()

    def collect_changes(self):
        self.fields = ["email", "first_name", "last_name", "role"]

        create_success_message("Employee", "created")
        self.update_table.append([f"Email: , {self.object.user.email}"])
        super().collect_changes()

    def go_back(self):
        call_command("employee")
        sys.exit()

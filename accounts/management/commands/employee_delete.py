import sys

from django.core.management import call_command
from accounts.models import Employee

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_invalid_error_message


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed for
    managing employee deletions within a system. It is specifically tailored
    for users with "MA" permissions, indicating that it is intended for
    managers.
    """

    help = "Prompts to delete an employee."
    action = "DELETE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Employee.objects.select_related("user").only("user__email").all()
        )

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

    def get_requested_model(self):
        while True:
            self.display_input_title("Enter details:")

            email = self.email_input("Email address")
            self.object = Employee.objects.filter(user__email=email).first()

            if self.object:
                break
            else:
                create_invalid_error_message("email")

        self.stdout.write()
        employee_table = [
            ["Email: ", self.object.user.email],
            ["First name: ", self.object.first_name],
            ["Last name: ", self.object.last_name],
            ["Role: ", self.object.get_role_display()],
        ]
        create_pretty_table(employee_table, "Details of the Employee:")

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {"delete": self.choice_str_input(
            ("Y", "N"), "Choice to delete [Y]es or [N]o")}

    def make_changes(self, data):
        if data["delete"] == "Y":
            self.object.user.delete()
        if data["delete"] == "N":
            self.stdout.write()
            call_command("employee")
            sys.exit()

    def go_back(self):
        call_command("employee")

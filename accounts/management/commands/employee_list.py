from django.core.management import call_command

from accounts.models import Employee

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed to list
    all employees within the system. It is accessible to users with "SA"
    (Sales), "SU" (Support), or "MA" (Management) permissions.
    """

    help = "Lists all employees."
    action = "LIST"
    permissions = ["SA", "SU", "MA"]

    def get_queryset(self):
        self.queryset = (Employee.objects.select_related("user")
                         .only("user__email").all())

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
            table_data, "Employees", headers=self.headers["employee"])

    def go_back(self):
        call_command("employee")

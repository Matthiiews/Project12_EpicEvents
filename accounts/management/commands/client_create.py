import sys

from django.db import IntegrityError
from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table
from cli.utils_messages import create_error_message, create_success_message

from accounts.models import Client


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed to
    facilitate the creation of new clients within a system. It is specifically
    tailored for users with "SA" permissions, indicating that it is intended
    for sales.
    """

    help = "Prompts for details to create a new client."
    action = "CREATE"
    permissions = ["SA"]

    def get_queryset(self):
        self.queryset = (Client.objects.select_related("employee")
                         .only("employee__first_name", "employee__last_name",
                               "employee__role").all())

    def get_instance_data(self):
        super().get_instance_data()

        all_clients_data = dict()
        my_clients_data = dict()

        for client in self.queryset:
            client_data = {
                "email": client.email,
                "name": client.get_full_name,
                "phone": client.phone,
                "company_name": client.company_name,
                "employee":
                    f"{client.employee.get_full_name} ({client.employee.role})"
            }

            all_clients_data[f"Client {client.id}"] = client_data

            if client.employee.user == self.user:
                # create a copy of 'client_date' otherwise the column
                # 'Employee' is empty
                client_data = client_data.copy()
                client_data.pop("employee", None)
                my_clients_data[f"Client {client.id}"] = client_data

        create_queryset_table(
            all_clients_data, "Clients", headers=self.headers["client"])
        # Remove "employee" from headers
        create_queryset_table(
            my_clients_data, "my Clients", headers=self.headers["client"][0:5])

    def get_data(self):
        self.display_input_title("Enter details to create a client:")

        return {
            "email": self.email_input("Email address"),
            "first_name": self.text_input("First name"),
            "last_name": self.text_input("Last name"),
            "phone": self.int_input("Phone number"),
            "company_name": self.text_input("Company name"),
        }

    def make_changes(self, data):
        try:
            self.object = Client.objects.create(
                employee=self.user.employee_users, **data)
        except IntegrityError:
            create_error_message("Email")
            call_command("client_create")
            sys.exit()

    def collect_changes(self):
        self.fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "company_name",
        ]

        create_success_message("Client", "created")
        super().collect_changes()

    def go_back(self):
        call_command("client")

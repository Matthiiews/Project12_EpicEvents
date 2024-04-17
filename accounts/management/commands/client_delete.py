import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_success_message

from accounts.models import Client


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed for
    managing client deletions within a system. It is specifically tailored for
    users with "MA" permissions, indicating that it is intended for managers.
    """
    help = "Prompts for details to delete a client."
    action = "DELETE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Client.objects.select_related("employee")
            .only("employee__first_name", "employee__last_name",
                  "employee__role").all())

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for client in self.queryset:
            client_data = {
                "email": client.email,
                "name": client.get_full_name,
                "phone": client.phone,
                "company_name": client.company_name,
                "employee":
                    f"{client.employee.get_full_name} ({client.employee.role})"
            }
            table_data[f"Client {client.id}"] = client_data
        create_queryset_table(
            table_data, "Clients", headers=self.headers["client"])

    def get_requested_model(self):
        self.display_input_title("Enter details:")

        email = self.email_input("Email address")
        self.stdout.write()
        self.object = Client.objects.filter(email=email).first()

        client_table = [
            ["Email: ", self.object.email],
            ["First name:", self.object.first_name],
            ["Last name:", self.object.last_name],
            ["Phone:", self.object.phone],
            ["Company name", self.object.company_name],
        ]

        create_pretty_table(client_table, "Details of the Client: ")

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {
            "delete": self.choice_str_input(
                ("Y", "N"), "Choice to delete [Y]es or [N]o ?")}

    def make_changes(self, data):
        if data["delete"] == "Y":
            self.object.delete()
        if data["delete"] == "N":
            self.stdout.write()
            call_command("client")
            sys.exit()

    def collect_changes(self):
        create_success_message("Client", "deleted")

    def go_back(self):
        call_command("clioent")

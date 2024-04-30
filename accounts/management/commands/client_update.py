from django.core.management import call_command

from accounts.models import Client

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)
from cli.utils_tables import create_queryset_table, create_pretty_table


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed for
    updating client details within a system. It is specifically tailored for
    users with "SA" permissions, indicating that it is intended for sales.
    """
    help = "Prompts for details to update a client."
    action = "UPDATE"
    permissions = ["SA"]

    def get_queryset(self):
        self.queryset = Client.objects.filter(employee__user=self.user).all()

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for client in self.queryset:
            client_data = {
                "email": client.email,
                "name": client.get_full_name,
                "phone": client.phone,
                "company_name": client.company_name,
            }
            table_data[f"Client {client.id}"] = client_data
        create_queryset_table(
            table_data, "my Clients", headers=self.headers["client"][0:5])

    def get_requested_model(self):
        while True:
            self.display_input_title("Enter details:")

            email = self.email_input("Email address")
            self.object = Client.objects.filter(email=email).first()

            if self.object:
                break
            else:
                create_invalid_error_message("email")

        self.stdout.write()
        client_table = [
            ["[E]mail: ", self.object.email],
            ["[F]irst name: ", self.object.first_name],
            ["[L]ast name: ", self.object.last_name],
            ["[P]hone: ", self.object.phone],
            ["[C]ompany name ", self.object.company_name],
        ]
        create_pretty_table(client_table, "Details of the Client: ")

    def get_fields_to_update(self):
        self.display_input_title("Enter choice:")

        self.fields_to_update = self.multiple_choice_str_input(
            ("E", "F", "L", "P", "C"), "Your choice ? [E, F, L, P, C]")

    def get_available_fields(self):
        self.available_fields = {
            "E": {
                "method": self.email_input,
                "params": {"label": "Email"},
                "label": "email",
            },
            "F": {
                "method": self.text_input,
                "params": {"label": "First name"},
                "label": "first_name",
            },
            "L": {
                "method": self.text_input,
                "params": {"label": "Last name"},
                "label": "last_name",
            },
            "P": {
                "method": self.int_input,
                "params": {"label": "Phone"},
                "label": "phone",
            },
            "C": {
                "method": self.text_input,
                "params": {"label": "Company name"},
                "label": "company_name",
            },
        }
        return self.available_fields

    def get_data(self):
        data = dict()
        for letter in self.fields_to_update:
            if self.available_fields[letter]:
                field_data = self.available_fields.get(letter)
                method = field_data["method"]
                params = field_data["params"]
                label = field_data["label"]

                data[label] = method(**params)
                self.fields.append(label)

        return data

    def make_changes(self, data):
        Client.objects.filter(email=self.object.email).update(**data)

        self.object.refresh_from_db()

        return self.object

    def collect_changes(self):
        self.fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "company_name"
        ]

        create_success_message("Client", "updated")
        super().collect_changes()

    def go_back(self):
        call_command("client")

import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_permission_denied_message

from accounts.models import Client


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed to list
    all clients with an option to filter the list based on user input. It is
    accessible to users with "SA", "SU", or "MA" permissions.
    """
    help = "Lists all clients."
    action = "LIST_FILTER"
    permissions = ["SA", "SU", "MA"]

    def get_queryset(self):
        self.queryset = (Client.objects.select_related("employee").all())

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

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {"filter": self.choice_str_input(
            ("Y", "N"), "Do you want to filter your clients ? [Y]es or [N]o")}

    def user_choice(self, choice):
        if choice["filter"] == "Y" and self.user.employee_users.role == "SA":
            self.stdout.write()
            return
        elif choice["filter"] == "Y":
            create_permission_denied_message()
            call_command("client")
            sys.exit()
        elif choice["filter"] == "N":
            self.stdout.write()
            call_command("client")
            sys.exit()

    def choose_attributes(self):
        self.fields = ["email", "first_name", "last_name", "company_name"]

        client_table = []
        for field in self.fields:
            field = field.replace("_", " ")
            formatted_field = [f"[{field[0].upper()}]{field[1:]}"]
            client_table.append(formatted_field)
        create_pretty_table(client_table, "Which fields you want to filter ?")

    def request_field_selection(self):
        self.display_input_title("Enter choice:")

        selected_fields = self.multiple_choice_str_input(
            ("E", "F", "L", "C"), "Your choice ? [E,F,L,C]")
        # ascending or descending
        order = self.choice_str_input(
            ("A", "D"), "Your choice ? [A]scending or [D]escending")
        self.stdout.write()

        return selected_fields, order

    def get_user_queryset(self):
        return self.queryset.filter(employee__user=self.user)

    def filter_selected_fields(self, selected_fields, order, user_queryset):
        field_mapping = {
            "E": "email",
            "F": "first_name",
            "L": "last_name",
            "C": "company_name",
        }

        order_by_fields = [
            f"{'_' if order == 'D' else ''}{field_mapping[field]}"
            for field in selected_fields
        ]

        filter_queryset = user_queryset.order_by(*order_by_fields)
        return filter_queryset, order_by_fields

    def display_result(self, filter_queryset, order_by_fields):
        table_data = dict()

        headers = ["", "** Client email **", "First name", "Last name",
                   "Company name"]

        for client in filter_queryset:
            client_data = {
                "email": client.email,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "company_name": client.company_name
            }
            table_data[f"Client {client.id}"] = client_data

        create_queryset_table(table_data, "my Clients", headers=headers,
                              order_by_fields=order_by_fields)

    def go_back(self):
        call_command("client")

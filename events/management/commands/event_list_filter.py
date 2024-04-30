import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_permission_denied_message

from events.models import Event


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed to list
    all events with an option to filter the list based on user input. It is
    accessible to users with "SA", "SU", or "MA" permissions.
    """

    help = "Lists all events."
    action = "LIST_FILTER"
    permissions = ["SA", "SU", "MA"]

    def get_queryset(self):
        self.queryset = (
            Event.objects.select_related("contract", "employee")
            .only("contract__client__email", "employee__first_name",
                  "employee__last_name", "employee__role").all())

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for event in self.queryset:
            event_data = {
                "client": event.contract.client.email,
                "date": event.date.strftime("%d/%m/%Y"),
                "name": event.name,
                "location": event.location,
                "max_guests": event.max_guests,
                "employee":
                    f"{event.employee.get_full_name} ({event.employee.role})",
            }
            table_data[f"Event {event.id}"] = event_data

        create_queryset_table(
            table_data, "Events", headers=self.headers["event"])

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {"filter": self.choice_str_input(
            ("Y", "N"), "Do you want to filter your clients? [Y]es or [N]o")}

    def user_choice(self, choice):
        if choice["filter"] == "Y" and self.user.employee_users.role == "SU":
            self.stdout.write()
            return
        elif choice["filter"] == "Y":
            create_permission_denied_message()
            call_command("event")
            sys.exit()
        elif choice["filter"] == "N":
            self.stdout.write()
            call_command("event")
            sys.exit()

    def choose_attributes(self):
        self.fields = [
            "client",
            "date",
            "name",
            "location",
            "max_guests",
        ]

        client_table = []
        for field in self.fields:
            field = field.replace("_", " ")
            formated_field = [f"[{field[0].upper()}]{field[1:]}"]
            client_table.append(formated_field)
        create_pretty_table(client_table, "Which fields you want to filter?")

    def request_field_selection(self):
        self.display_input_title("Enter choice:")

        selected_fields = self.multiple_choice_str_input(
            ("C", "D", "N", "L", "M"), "Your choice ? [C, D, N, L, M]")
        # ascending or descending
        order = self.choice_str_input(
            ("A", "D"), "Your choice ? [A]scending or [D]escending")
        self.stdout.write()
        return selected_fields, order

    def get_user_queryset(self):
        return self.queryset.filter(employee__user=self.user)

    def filter_selected_fields(self, selected_fields, order, user_queryset):
        field_mapping = {
            "C": "contract__client",
            "D": "date",
            "N": "name",
            "L": "location",
            "M": "max_guests",
        }

        order_by_fields = [
            f"{'-' if order == 'D' else ''}{field_mapping[field]}"
            for field in selected_fields]

        filter_queryset = user_queryset.order_by(*order_by_fields)

        return filter_queryset, order_by_fields

    def display_result(self, filter_queryset, order_by_fields):
        table_data = dict()

        headers = [
            "", "** Client email **", "Date", "Name", "Location", "Max_guests"]

        for event in filter_queryset:
            event_data = {
                "client": event.contract.client.email,
                "date": event.date.strftime("%d/%m/%Y"),
                "name": event.name,
                "location": event.location,
                "max_guests": event.max_guests,
            }
            table_data[f"Contract {event.id}"] = event_data

        create_queryset_table(
            table_data, "my Events", headers=headers,
            order_by_fields=order_by_fields)

    def go_back(self):
        call_command("event")

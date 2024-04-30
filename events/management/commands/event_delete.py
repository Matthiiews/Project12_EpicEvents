import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)

from events.models import Event


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed for
    managing event deletions within a system. It is specifically tailored for
    users with "MA" permissions, indicating that it is intended for managers.
    """

    help = "Prompts for details to delete an event."
    action = "DELETE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (Event.objects.select_related("contract")
                         .only("contract__client__email").all())

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for event in self.queryset:
            event_data = {
                "email": event.contract.client.email,
                "date": event.date.strftime("%d/%m/%Y"),
                "name": event.name,
                "location": event.location,
                "max_guests": event.max_guests,
            }
            table_data[f"Event {event.id}"] = event_data

        create_queryset_table(
            table_data, "Events", headers=self.headers["event"][0:6])

    def get_requested_model(self):
        while True:
            self.display_input_title("Enter details:")

            email = self.email_input("Email address of client")
            self.object = Event.objects.filter(
                contract__client__email=email).first()

            if self.object:
                break
            else:
                create_invalid_error_message("email")

        self.stdout.write()
        event_table = [
            ["Client: ", self.object.contract.client.email],
            ["Employee: ", self.object.employee.user.email],
            ["Date: ", self.object.date.strftime("%d/%m/%Y")],
            ["Name: ", self.object.name],
            ["Location: ", self.object.location],
            ["number of Guests: ", self.object.max_guests],
            ["Notes: ", self.object.notes],
        ]
        create_pretty_table(event_table, "Details of the Event: ")

    def get_data(self):
        self.display_input_title("Enter choice: ")

        return {"delete": self.choice_str_input(
            ("Y", "N"), "Choice to delete [Y]es or [N]o")}

    def make_changes(self, data):
        if data["delete"] == "Y":
            self.object.delete()
        if data["delete"] == "N":
            self.stdout.write()
            call_command("event")
            sys.exit()

    def collect_changes(self):
        create_success_message("Event", "deleted")

    def go_back(self):
        call_command("event")

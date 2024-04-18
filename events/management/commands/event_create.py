import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table
from cli.utils_messages import (
    create_does_not_exists_message, create_error_message,
    create_success_message)

from accounts.models import Employee, Client
from contracts.models import Contract
from events.models import Event


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed to
    facilitate the creation of new events within a system. It is specifically
    tailored for users with "SA" permissions, indicating that it is intended
    for sales.
    """

    help = "Prompts for details to create a new event"
    action = "CREATE"
    permissions = ["SA"]

    def get_queryset(self):
        self.employee = (Employee.objects.select_related("user")
                         .only("user__email").filter(role="SU"))
        self.client = Client.objects.filter(
            contract_clients__state="S").only("email")

    def get_instance_data(self):
        super().get_instance_data()

        all_su_employee_data = dict()
        all_client_data = dict()

        headers_su_employee = ["", "** Employee email **", "Role"]

        for employee in self.employee:
            su_employee_data = {
                "email": employee.user.email, "role": employee.role}
            all_su_employee_data[f"Employee {employee.id}"] = su_employee_data

        for client in self.client:
            client_data = {"email": client.email}
            all_client_data[f"Client {client.id}"] = client_data

        create_queryset_table(all_su_employee_data, "SU Employees",
                              headers=headers_su_employee)
        create_queryset_table(all_client_data, "Clients with signed contract",
                              headers=self.headers["client"][0:2])

    def get_data(self):
        self.display_input_title("Enter the details to create a new event:")

        return {
            "client": self.email_input("Client email"),
            "date": self.date_input("Date of the event [DD/MM/YYYY]"),
            "name": self.text_input("Name of the event"),
            "location": self.text_input("Location of the event"),
            "max_guests": self.int_input("Number of guests"),
            "notes": self.text_input("Any notes"),
            "employee": self.email_input("SU employee email"),
        }

    def make_changes(self, data):
        validated_data = dict()

        client = Client.objects.filter(email=data["client"]).first()
        employee = Employee.objects.filter(
            user__email=data["employee"]).first()
        contract = Contract.objects.filter(
            client__email=data["client"]).first()

        if not client:
            create_does_not_exists_message("Client")
            call_command("event_create")
            sys.exit()

        if not employee:
            create_does_not_exists_message("Employee")
            call_command("event_create")
            sys.exit()

        validated_data["client"] = client
        validated_data["employee"] = employee
        validated_data["contract"] = contract
        # remove client/employee from data dict, use validated_data dict
        # instead further:
        data.pop("client", None)
        data.pop("employee", None)

        # verify if event already exists:
        event_exists = Event.objects.filter(
            contract__client=validated_data["client"], name=data["name"]
            ).exists()

        if event_exists:
            create_error_message("Event")
            call_command("event_create")
            sys.exit()

        # create new event:
        self.object = Event.objects.create(
            contract=validated_data["contract"],
            employee=validated_data["employee"], **data)

    def collect_changes(self):
        self.fields = ["name", "location", "max_guests", "notes"]

        create_success_message("Event", "created")

        self.update_table.append(
            [f"Client: ", self.object.contract.client.email])
        self.update_table.append(
            [f"Employee: ", self.object.employee.user.email])
        self.update_table.append(
            [f"Date: ", self.object.date.strptime("%d/%m/%Y")])
        super().collect_changes()

    def go_back(self):
        call_command("event")

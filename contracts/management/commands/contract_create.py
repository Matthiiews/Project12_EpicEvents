import sys

from django.core.management import call_command


from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table
from cli.utils_messages import (
    create_does_not_exists_message, create_error_message,
    create_success_message)

from accounts.models import Client

from contracts.models import Contract


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed to
    facilitate the creation of new contract within a system. It is specifically
    tailored for users with "MA" permissions, indicating that it is intended
    for management.
    """

    help = "Prompts for details to create a new contract."
    action = "CREATE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Client.objects.select_related("employee")
            .only("employee__first_name", "employee__last_name",
                  "employee__role").filter(contract_clients__isnull=True).all()
        )

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

        create_queryset_table(table_data, "Clients without a contract",
                              headers=self.headers["client"])

    def get_data(self):
        self.display_input_title("Enter details to create a new contract:")

        return {
            "client": self.email_input("Client email"),
            "total_costs": self.decimal_input("Amount of contract"),
            "amount_paid": self.decimal_input("Paid amount"),
            "state": self.choice_str_input(
                ("S", "D"), "State [S]igned or [D]raft"),
        }

    def make_changes(self, data):
        validated_data = dict()
        # verify if the contract already exists, client + contract
        # OneToOne instead of ForeignKey? client

        client = Client.objects.filter(email=data["client"]).first()
        if not client:
            create_does_not_exists_message("Client")
            call_command("contract_create")
            sys.exit()

        validated_data["client"] = client
        validated_data["employee"] = client.employee

        # remove client and employee for data:
        data.pop("client", None)

        # verify if the contract already exists:
        contract_exists = Contract.objects.filter(
            client=validated_data["client"]).exists()
        if contract_exists:
            create_error_message("Contract")
            call_command("contract_create")
            sys.exit()

        # create the contract:
        self.object = Contract.objects.create(
            client=validated_data["client"],
            employee=validated_data["employee"], **data)

    def collect_changes(self):
        self.fields = ["total", "paid_amount", "rest_amount", "state"]

        create_success_message("Contract", "created")
        self.update_table.append([f"Client: ", self.object.client.email])
        self.update_table.append(
            [f"Employee: ", self.object.employee.user.email])
        super().collect_changes()

    def go_back(self):
        call_command("contract")

import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)

from contracts.models import Contract


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed for
    managing contract deletions within a system. It is specifically tailored
    for users with "MA" permissions, indicating that it is intended for
    managers.
    """

    help = "Prompts for details to delete a contract."
    action = "DELETE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (Contract.objects.select_related("client")
                         .only("client__email").all())

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for contract in self.queryset:
            contract_data = {
                "client": contract.client.email,
                "total": contract.total,
                "paid": contract.paid_amount,
                "rest": contract.rest_amount,
                "state": contract.get_state_display(),
            }
            table_data[f"Contract {contract.id}"] = contract_data

        create_queryset_table(table_data, "Contracts",
                              headers=self.headers["contract"][0:6])

    def get_requested_model(self):
        while True:
            self.display_input_title("Enter details:")

            email = self.email_input("Email address")
            self.object = Contract.objects.filter(client__email=email).first()

            if self.object:
                break
            else:
                create_invalid_error_message("email")

        self.stdout.write()
        contract_table = [
            ["Client: ", self.object.client.email],
            ["Employee: ", self.object.employee_user_email],
            ["Total costs: ", self.object.total],
            ["Amound paid: ", self.object.paid_amount],
            ["Rest amount: ", self.object.rest_amount],
            ["State: ", self.object.get_state_display()],
        ]
        create_pretty_table(contract_table, "Details of the Contract: ")

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {
            "delete": self.choice_str_input(
                ("Y", "N"), "Choice to delete [Y]es or [N]o")
        }

    def make_changes(self, data):
        if data["delete"] == "Y":
            self.object.delete()
        if data["delete"] == "N":
            self.stdout.write()
            call_command("contract")
            sys.exit()

    def collect_changes(self):
        create_success_message("Contract", "deleted")

    def go_back(self):
        call_command("contract")

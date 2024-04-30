from django.db import transaction
from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)

from accounts.models import Employee
from contracts.models import Contract


class Command(EpicEventsCommand):
    """
    This class `Command` is a subclass of `EpicEventsCommand` designed for
    updating contract details within a system. It is specifically tailored for
    users with "SA" and "MA" permissions, indicating that it is intended for
    sales and management.
    """

    help = "Prompts for details to update a contract."
    action = "UPDATE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Contract.objects.select_related("client").only("client__email")
            .all())

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

        create_queryset_table(
            table_data, "Contracts", headers=self.headers["contract"][0:6])

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
            ["[E]mployee: ", self.object.employee.user.email],
            ["[T]otal costs: ", self.object.total],
            ["[A]mount paid: ", self.object.paid_amount],
            ["Rest amount: ", self.object.rest_amount],
            ["[S]tate: ", self.object.get_state_display()],
        ]
        create_pretty_table(contract_table, "Details of the Contract: ")

    def get_fields_to_update(self):
        self.display_input_title("Enter choice:")

        self.fields_to_update = self.multiple_choice_str_input(
            ("E", "T", "A", "S"), "Your choice ? [E, T, A, S]")

    def get_available_fields(self):
        self.available_fields = {
            "E": {
                "method": self.email_input,
                "params": {"label": "Employee Email"},
                "label": "employee_email",
            },
            "T": {
                "method": self.decimal_input,
                "params": {"label": "Total amount"},
                "label": "total_costs",
            },
            "A": {
                "method": self.decimal_input,
                "params": {"label": "Amount paid"},
                "label": "amount_paid",
            },
            "S": {
                "method": self.choice_str_input,
                "params": {"options": ("S", "D"),
                           "label": "State [S]igned or [D]raft"},
                "label": "state",
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

    @transaction.atomic
    def make_changes(self, data):
        employee_email = data.pop("employee_email", None)
        employee = Employee.objects.filter(user__email=employee_email).first()

        if employee_email:
            contract = self.object
            contract.employee = employee
            contract.save()

        Contract.objects.filter(client=self.object.client).update(**data)

        # Refresh the object from the database
        self.object.refresh_from_db()

        return self.object

    def collect_changes(self):
        self.fields = ["total", "paid_amount", "rest_amount", "state"]

        create_success_message("Contract", "updated")
        self.update_table.append([f"Client: ", self.object.client.email])
        self.update_table.append([f"Employee: ", self.object.employee.user.email])
        super().collect_changes()

    def go_back(self):
        call_command("contract")

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
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour mettre à jour les détails des contrats dans un système. Elle est
    spécifiquement adaptée aux utilisateurs ayant les permissions "SA" (ventes)
    et "MA" (management), ce qui indique qu'elle est destinée aux ventes et à
    la gestion.

    - `help` : Une chaîne décrivant le but de la commande, qui consiste à
    demander les détails nécessaires pour mettre à jour un contrat.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "UPDATE".
    - `permissions` : Une liste de rôles autorisés à exécuter cette commande,
    dans ce cas, seuls "SA" (Ventes) et "MA" (Management) ont la permission.

    Les méthodes clés de cette classe comprennent :

    - `get_queryset` : Initialise le queryset pour les objets `Contrat`,
    sélectionnant les objets `Client` associés pour chaque contrat.
    - `get_create_model_table` : Génère une table de tous les contrats pour
    aider l'utilisateur à sélectionner un contrat à mettre à jour.
    - `get_requested_model` : Invite l'utilisateur à saisir l'adresse e-mail
    du client dont ils souhaitent mettre à jour le contrat et affiche les
    détails du contrat pour confirmation.
    - `get_fields_to_update` : Invite l'utilisateur à sélectionner les champs
    qu'ils souhaitent mettre à jour.
    - `get_available_fields` : Associe les champs sélectionnés à leurs
    méthodes de saisie correspondantes pour la collecte des données.
    - `get_data` : Collecte les nouvelles données pour les champs sélectionnés
    auprès de l'utilisateur.
    - `make_changes` : Met à jour le contrat avec les nouvelles données.
    - `collect_changes` : Confirme la mise à jour du contrat et affiche un
    message de succès.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des contrats.

    Cette classe encapsule la fonctionnalité de mise à jour des détails des
    contrats, en veillant à ce que seuls les utilisateurs ayant les
    permissions appropriées puissent effectuer cette action. Elle utilise la
    classe `EpicEventsCommand` pour les fonctionnalités de commande courantes,
    telles que l'affichage des invites de saisie et la gestion de la saisie
    utilisateur.
    """

    help = "Demande les détails nécessaires pour mettre à jour un contrat."
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

        # Actualise l'objet depuis la base de données.
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

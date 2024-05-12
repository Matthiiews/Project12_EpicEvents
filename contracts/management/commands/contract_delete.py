import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)

from contracts.models import Contract


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour gérer la suppression de contrats dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "MA",
    ce qui indique qu'elle est destinée aux gestionnaires.

    - `help` : Une chaîne décrivant le but de la commande, qui consiste à
    demander les détails nécessaires pour supprimer un contrat.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "DELETE".
    - `permissions` : Une liste de rôles autorisés à exécuter cette commande,
    dans ce cas, seul "MA" (Management) a la permission.

    Les méthodes clés de cette classe comprennent :

    - `get_create_model_table` : Génère un tableau de tous les contrats pour
    aider l'utilisateur à sélectionner un contrat à supprimer.
    - `get_requested_model` : Invite l'utilisateur à saisir l'adresse e-mail
    du client du contrat qu'il souhaite supprimer et affiche les détails du
    contrat pour confirmation.
    - `get_data` : Invite l'utilisateur à confirmer la suppression du contrat
    sélectionné.
    - `make_changes` : Si l'utilisateur confirme la suppression, il procède à
    la suppression du contrat ; sinon, il annule l'opération et retourne à
    l'interface de gestion des contrats.
    - `collect_changes` : Confirme la suppression du contrat et affiche un
    message de succès.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des contrats.

    Cette classe encapsule la fonctionnalité de suppression de contrats, en
    veillant à ce que seuls les utilisateurs disposant des permissions
    appropriées puissent effectuer cette action. Elle exploite la classe
    `EpicEventsCommand` pour les fonctionnalités de commande courantes, telles
    que l'affichage des invites de saisie et la gestion de la saisie
    utilisateur.
    """

    help = "Demande des détails pour supprimer un contrat."
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
            ["Employee: ", self.object.employee.user.email],
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

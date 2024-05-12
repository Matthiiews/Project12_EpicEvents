import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_success_message

from accounts.models import Client


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour gérer les suppressions de clients dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "MA",
    indiquant qu'elle est destinée aux managers.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    demander les détails nécessaires pour supprimer un client.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "DELETE".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, seule "MA" (Management) a la permission.

    Les principales méthodes de cette classe incluent :

    - `get_create_model_table` : Génère une table de tous les e-mails des
    clients pour aider l'utilisateur à sélectionner un client à supprimer.
    - `get_requested_model` : Invite l'utilisateur à saisir l'adresse e-mail
    du client qu'il souhaite supprimer et affiche les détails du client pour
    confirmation.
    - `get_data` : Invite l'utilisateur à confirmer la suppression du client
    sélectionné.
    - `make_changes` : Si l'utilisateur confirme la suppression, il procède à
    la suppression du client ; sinon, il annule l'opération et retourne à
    l'interface de gestion des clients.
    - `collect_changes` : Confirme la suppression du client et affiche un
    message de réussite.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des clients.

    Cette classe encapsule la fonctionnalité pour supprimer des clients, en
    veillant à ce que seuls les utilisateurs disposant des permissions
    appropriées puissent effectuer cette action. Elle tire parti de la classe
    `EpicEventsCommand` pour les fonctionnalités de commande communes, telles
    que l'affichage des invites de saisie et la gestion de la saisie
    utilisateur.
    """
    help = "Demande les détails pour supprimer un client."
    action = "DELETE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Client.objects.select_related("employee")
            .only("employee__first_name", "employee__last_name",
                  "employee__role").all())

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

    def get_requested_model(self):
        self.display_input_title("Enter details:")

        email = self.email_input("Email address")
        self.stdout.write()
        self.object = Client.objects.filter(email=email).first()

        client_table = [
            ["Email: ", self.object.email],
            ["First name:", self.object.first_name],
            ["Last name:", self.object.last_name],
            ["Phone:", self.object.phone],
            ["Company name", self.object.company_name],
        ]

        create_pretty_table(client_table, "Details of the Client: ")

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {
            "delete": self.choice_str_input(
                ("Y", "N"), "Choice to delete [Y]es or [N]o ?")}

    def make_changes(self, data):
        if data["delete"] == "Y":
            self.object.delete()
        if data["delete"] == "N":
            self.stdout.write()
            call_command("client")
            sys.exit()

    def collect_changes(self):
        create_success_message("Client", "deleted")

    def go_back(self):
        call_command("clioent")

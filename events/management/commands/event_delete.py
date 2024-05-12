import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)

from events.models import Event


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour gérer les suppressions d'événements dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "MA",
    ce qui indique qu'elle est destinée aux gestionnaires.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    demander les détails nécessaires pour supprimer un événement.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "DELETE".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, seul "MA" (Management) a la permission.

    Les méthodes clés de cette classe incluent :

    - `get_create_model_table` : Génère un tableau de tous les événements pour
    aider l'utilisateur à sélectionner un événement à supprimer.
    - `get_requested_model` : Demande à l'utilisateur de saisir l'adresse
    e-mail du client correspondant à l'événement qu'ils souhaitent supprimer
    et affiche les détails de l'événement pour confirmation.
    - `get_data` : Demande à l'utilisateur de confirmer la suppression de
    l'événement sélectionné.
    - `make_changes` : Si l'utilisateur confirme la suppression, il procède à
    la suppression de l'événement ; sinon, il annule l'opération et retourne à
    l'interface de gestion des événements.
    - `collect_changes` : Confirme la suppression de l'événement et affiche un
    message de succès.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des événements.

    Cette classe encapsule la fonctionnalité de suppression des événements, en
    veillant à ce que seuls les utilisateurs disposant des permissions
    appropriées puissent effectuer cette action. Elle exploite la classe
    `EpicEventsCommand` pour des fonctionnalités de commande communes, telles
    que l'affichage des invites de saisie et la gestion de la saisie
    utilisateur.
    """

    help = "Demande les détails pour supprimer un événement."
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

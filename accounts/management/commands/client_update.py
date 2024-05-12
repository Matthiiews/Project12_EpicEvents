from django.core.management import call_command

from accounts.models import Client

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)
from cli.utils_tables import create_queryset_table, create_pretty_table


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour mettre à jour les détails des clients dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "SA",
    indiquant qu'elle est destinée aux ventes.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    demander les détails nécessaires pour mettre à jour un client.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "UPDATE".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, seul "SA" (Ventes) a la permission.

    Les principales méthodes de cette classe incluent :

    - `get_queryset` : Initialise le queryset pour les objets `Client`, en
    sélectionnant les objets `Employee` associés à chaque événement.
    - `get_create_model_table` : Génère une table de tous les e-mails des
    clients pour aider l'utilisateur à sélectionner un client à mettre à jour.
    - `get_requested_model` : Invite l'utilisateur à saisir l'adresse e-mail
    du client qu'il souhaite mettre à jour et affiche les détails du client
    pour confirmation.
    - `get_fields_to_update` : Invite l'utilisateur à sélectionner les champs
    qu'il souhaite mettre à jour.
    - `get_available_fields` : Associe les champs sélectionnés à leurs
    méthodes d'entrée correspondantes pour la collecte de données.
    - `get_data` : Collecte les nouvelles données pour les champs sélectionnés
    auprès de l'utilisateur.
    - `make_changes` : Met à jour le client avec les nouvelles données.
    - `collect_changes` : Confirme la mise à jour du client et affiche un
    message de réussite.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des clients.

    Cette classe encapsule la fonctionnalité pour mettre à jour les détails
    des clients, en veillant à ce que seuls les utilisateurs disposant des
    permissions appropriées puissent effectuer cette action. Elle tire parti
    de la classe `EpicEventsCommand` pour les fonctionnalités de commande
    communes, telles que l'affichage des invites de saisie et la gestion de la
    saisie utilisateur.
    """
    help = "Demande les détails pour mettre à jour un client."
    action = "UPDATE"
    permissions = ["SA"]

    def get_queryset(self):
        self.queryset = Client.objects.filter(employee__user=self.user).all()

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for client in self.queryset:
            client_data = {
                "email": client.email,
                "name": client.get_full_name,
                "phone": client.phone,
                "company_name": client.company_name,
            }
            table_data[f"Client {client.id}"] = client_data
        create_queryset_table(
            table_data, "my Clients", headers=self.headers["client"][0:5])

    def get_requested_model(self):
        while True:
            self.display_input_title("Enter details:")

            email = self.email_input("Email address")
            self.object = Client.objects.filter(email=email).first()

            if self.object:
                break
            else:
                create_invalid_error_message("email")

        self.stdout.write()
        client_table = [
            ["[E]mail: ", self.object.email],
            ["[F]irst name: ", self.object.first_name],
            ["[L]ast name: ", self.object.last_name],
            ["[P]hone: ", self.object.phone],
            ["[C]ompany name ", self.object.company_name],
        ]
        create_pretty_table(client_table, "Details of the Client: ")

    def get_fields_to_update(self):
        self.display_input_title("Enter choice:")

        self.fields_to_update = self.multiple_choice_str_input(
            ("E", "F", "L", "P", "C"), "Your choice ? [E, F, L, P, C]")

    def get_available_fields(self):
        self.available_fields = {
            "E": {
                "method": self.email_input,
                "params": {"label": "Email"},
                "label": "email",
            },
            "F": {
                "method": self.text_input,
                "params": {"label": "First name"},
                "label": "first_name",
            },
            "L": {
                "method": self.text_input,
                "params": {"label": "Last name"},
                "label": "last_name",
            },
            "P": {
                "method": self.int_input,
                "params": {"label": "Phone"},
                "label": "phone",
            },
            "C": {
                "method": self.text_input,
                "params": {"label": "Company name"},
                "label": "company_name",
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

    def make_changes(self, data):
        Client.objects.filter(email=self.object.email).update(**data)

        self.object.refresh_from_db()

        return self.object

    def collect_changes(self):
        self.fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "company_name"
        ]

        create_success_message("Client", "updated")
        super().collect_changes()

    def go_back(self):
        call_command("client")

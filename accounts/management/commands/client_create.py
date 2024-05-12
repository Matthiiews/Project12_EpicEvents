import sys

from django.db import IntegrityError
from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table
from cli.utils_messages import create_error_message, create_success_message

from accounts.models import Client


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour faciliter la création de nouveaux clients dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "SA",
    indiquant qu'elle est destinée aux ventes.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    demander les détails nécessaires à la création d'un nouveau client.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "CREATE".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, seule "SA" (Ventes) a la permission.

    Les principales méthodes de cette classe incluent :

    - `get_queryset` : Initialise le queryset pour les objets `Client`,
    en sélectionnant les objets `Employee` associés à chaque client.
    - `get_create_model_table` : Génère des tables de tous les clients et un
    sous-ensemble de clients liés à l'utilisateur actuel, affichant des
    informations pertinentes telles que l'e-mail, le prénom, le nom de famille,
    le nom de la société et l'employé.
    - `get_data` : Invite l'utilisateur à saisir les détails pour créer un
    nouveau client, capturant l'e-mail, le prénom, le nom de famille, le
    numéro de téléphone et le nom de la société.
    - `make_changes` : Tente de créer un nouvel objet `Client` avec les
    données fournies, en l'associant à l'objet `Employee` de l'utilisateur
    actuel. Gère les éventuelles `IntegrityError` en affichant un message
    d'erreur et en redemandant à l'utilisateur de créer un client.
    - `collect_changes` : Confirme la création d'un nouveau client et affiche
    un message de réussite.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des clients.

    Cette classe encapsule la fonctionnalité pour créer de nouveaux clients,
    en veillant à ce que seuls les utilisateurs disposant des permissions
    appropriées puissent effectuer cette action. Elle tire parti de la classe
    `EpicEventsCommand` pour les fonctionnalités de commande communes, telles
    que l'affichage des invites de saisie et la gestion de la saisie
    utilisateur.
    """

    help = "Demande les détails pour créer un nouveau client."
    action = "CREATE"
    permissions = ["SA"]

    def get_queryset(self):
        self.queryset = (Client.objects.select_related("employee")
                         .only("employee__first_name", "employee__last_name",
                               "employee__role").all())

    def get_instance_data(self):
        super().get_instance_data()

        all_clients_data = dict()
        my_clients_data = dict()

        for client in self.queryset:
            client_data = {
                "email": client.email,
                "name": client.get_full_name,
                "phone": client.phone,
                "company_name": client.company_name,
                "employee":
                    f"{client.employee.get_full_name} ({client.employee.role})"
            }

            all_clients_data[f"Client {client.id}"] = client_data

            if client.employee.user == self.user:
                # Créez une copie de 'client_date' sinon la colonne 'Employé'
                # est vide.
                client_data = client_data.copy()
                client_data.pop("employee", None)
                my_clients_data[f"Client {client.id}"] = client_data

        create_queryset_table(
            all_clients_data, "Clients", headers=self.headers["client"])
        # Supprimez "employé" des en-têtes.
        create_queryset_table(
            my_clients_data, "my Clients", headers=self.headers["client"][0:5])

    def get_data(self):
        self.display_input_title("Enter details to create a client:")

        return {
            "email": self.email_input("Email address"),
            "first_name": self.text_input("First name"),
            "last_name": self.text_input("Last name"),
            "phone": self.int_input("Phone number"),
            "company_name": self.text_input("Company name"),
        }

    def make_changes(self, data):
        try:
            self.object = Client.objects.create(
                employee=self.user.employee_users, **data)
        except IntegrityError:
            create_error_message("Email")
            call_command("client_create")
            sys.exit()

    def collect_changes(self):
        self.fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "company_name",
        ]

        create_success_message("Client", "created")
        super().collect_changes()

    def go_back(self):
        call_command("client")

import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_permission_denied_message

from accounts.models import Client


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour répertorier tous les clients avec une option pour filtrer la liste en
    fonction de l'entrée de l'utilisateur. Elle est accessible aux
    utilisateurs disposant des permissions "SA", "SU" ou "MA".

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    répertorier tous les clients et éventuellement les filtrer.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "LIST_FILTER".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, "SA" (Ventes), "SU" (Support) et "MA" (Management) ont la
    permission.

    Les principales méthodes de cette classe incluent :

    - `get_queryset` : Initialise le queryset pour les objets `Client`, en
    sélectionnant les objets `Employee` associés à chaque client.
    - `get_create_model_table` : Génère une table de tous les clients,
    affichant des informations pertinentes telles que l'e-mail, le prénom, le
    nom de famille, le nom de la société et l'employé.
    - `get_data` : Invite l'utilisateur à décider s'il souhaite filtrer les
    clients, capturant leur choix.
    - `user_choice` : Gère le choix de l'utilisateur de filtrer les clients,
    avec une gestion spéciale pour le rôle "SA" pour permettre le filtrage
    sans messages d'interdiction de permission.
    - `choose_attributes` : Affiche les champs disponibles pour le filtrage et
    permet à l'utilisateur de sélectionner les champs par lesquels il souhaite
    filtrer.
    - `request_field_selection` : Invite l'utilisateur à sélectionner des
    champs spécifiques pour le filtrage et à choisir l'ordre
    (ascendant ou descendant).
    - `get_user_queryset` : Filtre le queryset en fonction de la sélection de
    l'utilisateur et de sa préférence d'ordre.
    - `filter_selected_fields` : Applique les filtres et l'ordre sélectionnés
    au queryset, le préparant pour l'affichage.
    - `display_result` : Affiche la liste filtrée et ordonnée des clients à
    l'utilisateur.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des clients.

    Cette classe encapsule la fonctionnalité pour répertorier et
    éventuellement filtrer les clients, en veillant à ce que seuls les
    utilisateurs disposant des permissions appropriées puissent effectuer ces
    actions. Elle tire parti de la classe `EpicEventsCommand` pour les
    fonctionnalités de commande communes, telles que l'affichage des invites
    de saisie et la gestion de la saisie utilisateur..
    """
    help = "Liste de tous les clients."
    action = "LIST_FILTER"
    permissions = ["SA", "SU", "MA"]

    def get_queryset(self):
        self.queryset = (Client.objects.select_related("employee").all())

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

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {"filter": self.choice_str_input(
            ("Y", "N"), "Do you want to filter your clients ? [Y]es or [N]o")}

    def user_choice(self, choice):
        if choice["filter"] == "Y" and self.user.employee_users.role == "SA":
            self.stdout.write()
            return
        elif choice["filter"] == "Y":
            create_permission_denied_message()
            call_command("client")
            sys.exit()
        elif choice["filter"] == "N":
            self.stdout.write()
            call_command("client")
            sys.exit()

    def choose_attributes(self):
        self.fields = ["email", "first_name", "last_name", "company_name"]

        client_table = []
        for field in self.fields:
            field = field.replace("_", " ")
            formatted_field = [f"[{field[0].upper()}]{field[1:]}"]
            client_table.append(formatted_field)
        create_pretty_table(client_table, "Which fields you want to filter ?")

    def request_field_selection(self):
        self.display_input_title("Enter choice:")

        selected_fields = self.multiple_choice_str_input(
            ("E", "F", "L", "C"), "Your choice ? [E,F,L,C]")
        # ascending or descending
        order = self.choice_str_input(
            ("A", "D"), "Your choice ? [A]scending or [D]escending")
        self.stdout.write()

        return selected_fields, order

    def get_user_queryset(self):
        return self.queryset.filter(employee__user=self.user)

    def filter_selected_fields(self, selected_fields, order, user_queryset):
        field_mapping = {
            "E": "email",
            "F": "first_name",
            "L": "last_name",
            "C": "company_name",
        }

        order_by_fields = [
            f"{'_' if order == 'D' else ''}{field_mapping[field]}"
            for field in selected_fields
        ]

        filter_queryset = user_queryset.order_by(*order_by_fields)
        return filter_queryset, order_by_fields

    def display_result(self, filter_queryset, order_by_fields):
        table_data = dict()

        headers = ["", "** Client email **", "First name", "Last name",
                   "Company name"]

        for client in filter_queryset:
            client_data = {
                "email": client.email,
                "first_name": client.first_name,
                "last_name": client.last_name,
                "company_name": client.company_name
            }
            table_data[f"Client {client.id}"] = client_data

        create_queryset_table(table_data, "my Clients", headers=headers,
                              order_by_fields=order_by_fields)

    def go_back(self):
        call_command("client")

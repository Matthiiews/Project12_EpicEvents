import sys

from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_permission_denied_message

from events.models import Event


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour répertorier tous les événements avec une option pour filtrer la liste
    en fonction de l'entrée de l'utilisateur. Elle est accessible aux
    utilisateurs avec les permissions "SA", "SU" ou "MA".

    - `help`: Une chaîne décrivant l'objectif de la commande, qui est de
    répertorier tous les événements et éventuellement de les filtrer.
    - `action`: Une chaîne indiquant l'action associée à cette commande,
    définie sur "LIST_FILTER".
    - `permissions`: Une liste de rôles autorisés à exécuter cette commande,
    dans ce cas, "SA" (Ventes), "SU" (Support) et "MA" (Management)
    ont la permission.

    Les principales méthodes de cette classe comprennent :

    - `get_queryset`: Initialise le queryset pour les objets `Event`,
    sélectionnant les objets `Contract` et `Employee` associés à chaque
    événement.
    - `get_create_model_table`: Génère un tableau de tous les événements,
    affichant des informations pertinentes telles que l'e-mail du client,
    la date, le nom, l'emplacement, le nombre maximal d'invités et l'employé.
    - `get_data`: Demande à l'utilisateur s'il souhaite filtrer les événements,
    en capturant leur choix.
    - `user_choice`: Gère le choix de l'utilisateur pour filtrer les
    événements, avec une manipulation spéciale pour les rôles "SA" et "SU"
    pour permettre le filtrage sans messages d'autorisation refusée.
    - `choose_attributes`: Affiche les champs disponibles pour le filtrage et
    permet à l'utilisateur de sélectionner les champs à filtrer.
    - `request_field_selection`: Invite l'utilisateur à sélectionner des
    champs spécifiques pour le filtrage et à choisir l'ordre
    (ascendant ou descendant).
    - `get_user_queryset`: Filtre le queryset en fonction de la sélection et
    des préférences d'ordre de l'utilisateur.
    - `filter_selected_fields`: Applique les filtres et l'ordre sélectionnés
    au queryset, le préparant pour l'affichage.
    - `display_result`: Affiche la liste filtrée et triée des événements à
    l'utilisateur.
    - `go_back`: Fournit une option pour revenir à la commande précédente,
    probablement à l'interface principale de gestion des événements.

    Cette classe encapsule la fonctionnalité pour répertorier et
    éventuellement filtrer les événements, garantissant que seuls les
    utilisateurs ayant les permissions appropriées peuvent effectuer ces
    actions. Elle tire parti de la classe `EpicEventsCommand` pour les
    fonctionnalités communes des commandes, telles que l'affichage des invites
    de saisie et la gestion de l'entrée utilisateur.
    """

    help = "Listes de tous les événements."
    action = "LIST_FILTER"
    permissions = ["SA", "SU", "MA"]

    def get_queryset(self):
        self.queryset = (
            Event.objects.select_related("contract", "employee")
            .only("contract__client__email", "employee__first_name",
                  "employee__last_name", "employee__role").all())

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for event in self.queryset:
            event_data = {
                "client": event.contract.client.email,
                "date": event.date.strftime("%d/%m/%Y"),
                "name": event.name,
                "location": event.location,
                "max_guests": event.max_guests,
                "employee":
                    f"{event.employee.get_full_name} ({event.employee.role})",
            }
            table_data[f"Event {event.id}"] = event_data

        create_queryset_table(
            table_data, "Events", headers=self.headers["event"])

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {"filter": self.choice_str_input(
            ("Y", "N"), "Do you want to filter your clients? [Y]es or [N]o")}

    def user_choice(self, choice):
        if choice["filter"] == "Y" and self.user.employee_users.role == "SU":
            self.stdout.write()
            return
        elif choice["filter"] == "Y":
            create_permission_denied_message()
            call_command("event")
            sys.exit()
        elif choice["filter"] == "N":
            self.stdout.write()
            call_command("event")
            sys.exit()

    def choose_attributes(self):
        self.fields = [
            "client",
            "date",
            "name",
            "location",
            "max_guests",
        ]

        client_table = []
        for field in self.fields:
            field = field.replace("_", " ")
            formated_field = [f"[{field[0].upper()}]{field[1:]}"]
            client_table.append(formated_field)
        create_pretty_table(client_table, "Which fields you want to filter?")

    def request_field_selection(self):
        self.display_input_title("Enter choice:")

        selected_fields = self.multiple_choice_str_input(
            ("C", "D", "N", "L", "M"), "Your choice ? [C, D, N, L, M]")
        # ascending or descending
        order = self.choice_str_input(
            ("A", "D"), "Your choice ? [A]scending or [D]escending")
        self.stdout.write()
        return selected_fields, order

    def get_user_queryset(self):
        return self.queryset.filter(employee__user=self.user)

    def filter_selected_fields(self, selected_fields, order, user_queryset):
        field_mapping = {
            "C": "contract__client",
            "D": "date",
            "N": "name",
            "L": "location",
            "M": "max_guests",
        }

        order_by_fields = [
            f"{'-' if order == 'D' else ''}{field_mapping[field]}"
            for field in selected_fields]

        filter_queryset = user_queryset.order_by(*order_by_fields)

        return filter_queryset, order_by_fields

    def display_result(self, filter_queryset, order_by_fields):
        table_data = dict()

        headers = [
            "", "** Client email **", "Date", "Name", "Location", "Max_guests"]

        for event in filter_queryset:
            event_data = {
                "client": event.contract.client.email,
                "date": event.date.strftime("%d/%m/%Y"),
                "name": event.name,
                "location": event.location,
                "max_guests": event.max_guests,
            }
            table_data[f"Contract {event.id}"] = event_data

        create_queryset_table(
            table_data, "my Events", headers=headers,
            order_by_fields=order_by_fields)

    def go_back(self):
        call_command("event")

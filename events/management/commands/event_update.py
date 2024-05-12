from django.core.management import call_command
from django.db import transaction

from accounts.models import Employee
from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import (
    create_invalid_error_message, create_success_message)

from events.models import Event


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour mettre à jour les détails des événements dans un système. Elle est
    spécifiquement conçue pour les utilisateurs ayant les permissions "SA" et
    "MA", ce qui indique qu'elle est destinée aux ventes et à la gestion.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui est de
    demander les détails nécessaires pour mettre à jour un événement.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "UPDATE".
    - `permissions` : Une liste de rôles autorisés à exécuter cette commande,
    dans ce cas, seuls les "SA" (ventes) et "MA" (gestion) ont la permission.

    Les méthodes clés de cette classe incluent :
    - `get_queryset` : Initialise le queryset pour les objets `Event`,
    sélectionnant les objets `Client` associés pour chaque événement.
    - `get_create_model_table` : Génère un tableau de tous les événements pour
    aider l'utilisateur à sélectionner un événement à mettre à jour.
    - `get_requested_model` : Invite l'utilisateur à saisir l'adresse e-mail
    du client de l'événement qu'ils souhaitent mettre à jour et affiche les
    détails de l'événement pour confirmation.
    - `get_fields_to_update` : Invite l'utilisateur à sélectionner les champs
    qu'il souhaite mettre à jour.
    - `get_available_fields` : Associe les champs sélectionnés à leurs
    méthodes de saisie correspondantes pour la collecte de données.
    - `get_data` : Collecte les nouvelles données pour les champs sélectionnés
    par l'utilisateur.
    - `make_changes` : Met à jour l'événement avec les nouvelles données.
    - `collect_changes` : Confirme la mise à jour de l'événement et affiche un
    message de succès.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des événements.

    Cette classe encapsule la fonctionnalité de mise à jour des détails de
    l'événement, garantissant que seuls les utilisateurs ayant les permissions
    appropriées peuvent effectuer cette action. Elle utilise la classe
    `EpicEventsCommand` pour les fonctionnalités communes de commande, telles
    que l'affichage des invitations à saisir et la gestion de la saisie
    utilisateur.
    """

    help = "Invite à fournir des détails pour mettre à jour un événement."
    action = "UPDATE"
    permissions = ["SU", "MA"]

    def get_queryset(self):
        if self.user.employee_users.role == "SU":
            queryset = (Event.objects.select_related("contract")
                        .only("contract__client__email")
                        .filter(employee__user=self.user).all())
        else:
            queryset = (
                Event.objects.select_related("contract", "employee")
                .only("contract__client__email", "employee__first_name",
                      "employee__last_name", "employee__role").all())
        self.queryset = queryset

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

        if self.user.employee_users.role == "MA":
            create_queryset_table(
                table_data, "my Events", headers=self.headers["event"])
        else:
            create_queryset_table(
                table_data, "my Events", headers=self.headers["event"][0:6])

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
            ["[E]mployee: ", self.object.employee.user.email],
            ["[D]ate: ", self.object.date.strftime("%d/%m/%Y")],
            ["[N]ame: ", self.object.name],
            ["[L]ocation: ", self.object.location],
            ["number of [G]uests: ", self.object.max_guests],
            ["[No]otes: ", self.object.notes],
        ]
        create_pretty_table(event_table, "Details of the Event: ")

    def get_fields_to_update(self):
        self.display_input_title("Enter choice:")

        self.fields_to_update = self.multiple_choice_str_input(
            ("E", "D", "N", "L", "G", "No"),
            "Your choice ? [E, D, N, L, G, No]")

    def get_available_fields(self):
        self.available_fields = {
            "E": {
                "method": self.email_input,
                "params": {"label": "Employee Email"},
                "label": "employee_email",
            },
            "D": {
                "method": self.date_input,
                "params": {"label": "Date of the event"},
                "label": "date",
            },
            "N": {
                "method": self.text_input,
                "params": {"label": "name of event"},
                "label": "name",
            },
            "L": {
                "method": self.text_input,
                "params": {"label": "Location of the event"},
                "label": "location",
            },
            "G": {
                "method": self.text_input,
                "params": {"label": "Number of guest"},
                "label": "max_guests",
            },
            "No": {
                "method": self.text_input,
                "params": {"label": "Notes of the event"},
                "label": "notes",
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
            event = self.object
            event.employee = employee
            event.save()

        Event.objects.filter(
            contract__client=self.object.contract.client).update(**data)

        # Actualise l'objet depuis la base de données.
        self.object.refresh_from_db()

        return self.object

    def collect_changes(self):
        self.fields = ["name", "location", "max_guests", "notes"]

        create_success_message("Event", "created")

        self.update_table.append(
            [f"Client: ", self.object.contract.client.email])
        self.update_table.append(
            [f"Employee: ", self.object.employee.user.email])
        self.update_table.append(
            [f"Date: ", self.object.date.strftime("%d/%m/%Y")])
        super().collect_changes()

    def go_back(self):
        call_command("event")

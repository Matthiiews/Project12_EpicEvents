import sys

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import transaction

from accounts.models import Employee

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import (
    create_invalid_error_message, create_error_message, create_success_message)

UserModel = get_user_model()


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour mettre à jour les détails des employés dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "MA", ce
    qui indique qu'elle est destinée à la gestion.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    demander les détails nécessaires pour mettre à jour un employé.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "UPDATE".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, seul "MA" (Management) a la permission.

    Les principales méthodes de cette classe incluent :

    - `get_queryset` : Initialise le queryset pour les objets `Employee`, en
    sélectionnant les objets `User` associés à chaque employé.
    - `get_create_model_table` : Génère une table de tous les e-mails des
    employés pour aider l'utilisateur à sélectionner un employé à mettre à
    jour.
    - `get_requested_model` : Invite l'utilisateur à saisir l'adresse e-mail
    de l'employé qu'il souhaite mettre à jour et affiche les détails de
    l'employé pour confirmation.
    - `get_fields_to_update` : Invite l'utilisateur à sélectionner les champs
    qu'il souhaite mettre à jour.
    - `get_available_fields` : Associe les champs sélectionnés à leurs
    méthodes d'entrée correspondantes pour la collecte de données.
    - `get_data` : Collecte les nouvelles données pour les champs sélectionnés
    auprès de l'utilisateur.
    - `make_changes` : Met à jour l'employé avec les nouvelles données.
    - `collect_changes` : Confirme la mise à jour de l'employé et affiche un
    message de réussite.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des employés.

    Cette classe encapsule la fonctionnalité pour mettre à jour les détails
    des employés, en veillant à ce que seuls les utilisateurs disposant des
    permissions appropriées puissent effectuer cette action. Elle tire parti
    de la classe `EpicEventsCommand` pour les fonctionnalités de commande
    communes, telles que l'affichage des invites de saisie et la gestion de la
    saisie utilisateur.
    """

    help = "Invite à mettre à jour un employé."
    action = "UPDATE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Employee.objects.select_related("user").only("user__email").all())

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for employee in self.queryset:
            employee_data = {
                "email": employee.user.email,
                "first_name": employee.get_full_name,
                "role": employee.role,
            }
            table_data[f"Employee {employee.id}"] = employee_data

        create_queryset_table(
            table_data, "Employees", headers=self.headers["employee"])

    def get_requested_model(self):
        while True:
            self.display_input_title("Enter details:")

            email = self.email_input("Email address")
            self.object = Employee.objects.filter(user__email=email).first()

            if self.object:
                break
            else:
                create_invalid_error_message("email")

        self.stdout.write()
        employee_table = [
            ["[E]mail: ", self.object.user.email],
            ["[F]irst name: ", self.object.first_name],
            ["[L]ast name: ", self.object.last_name],
            ["[R]ole: ", self.object.get_role_display()],
        ]
        create_pretty_table(employee_table, "Details of the Employee: ")

    def get_fields_to_update(self):
        self.display_input_title("Enter choice:")

        self.fields_to_update = self.multiple_choice_str_input(
            ("E", "F", "L", "R"), "Your choice ? [E, F, L, R]")

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
                "label": "first name",
            },
            "L": {
                "method": self.text_input,
                "params": {"label": "Last name"},
                "label": "last_name",
            },
            "R": {
                "method": self.choice_str_input,
                "params": {"options": ("SA", "SU", "MA"),
                           "label": "Role: [SA]les, [SU]pport or [MA]nagement",
                           },
                "label": "role",
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
    # Si l'email de l'utilisateur est enregistré et que la mise à jour de
    # l'employé ne fonctionne pas, l'email de l'utilisateur restera enregistré
    # mais la mise à jour de l'employé échouera avec transaction.atomic, les
    # deux seront annulés.
    def make_changes(self, data):
        email = data.pop("email", None)

        if email:
            if UserModel.objects.filter(email=email).exists():
                create_error_message("This email")
                call_command("employee_update")
                sys.exit()
            else:
                user = self.object.user
                user.email = email
                user.save()

        Employee.objects.filter(user=self.object.user).update(**data)

        # Rafraîchir l'objet à partir de la base de données
        self.object.refresh_from_db()

        return self.object

    def collect_changes(self):
        self.fields = ["email", "first_name", "last_name", "role"]

        create_success_message("Employee", "updated")

        self.update_table.append([f"Email: ", self.object.user.email])
        super().collect_changes()

    def go_back(self):
        call_command("employee")

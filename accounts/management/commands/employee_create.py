import sys

from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.core.management import call_command

from accounts.models import Employee

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table
from cli.utils_messages import create_error_message, create_success_message


UserModel = get_user_model()


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour faciliter la création de nouveaux employés dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "MA", ce
    qui indique qu'elle est destinée à la gestion.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    demander les détails nécessaires pour créer un nouvel employé.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "CREATE".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, seul "MA" (Management) a la permission.

    Les principales méthodes de cette classe incluent :

    - `get_queryset` : Initialise le queryset pour les objets `Employee`, en
    sélectionnant les objets `User` associés à chaque employé.
    - `get_create_model_table` : Génère des tables de tous les employés et d'un
    sous-ensemble d'employés liés à l'utilisateur actuel, affichant des
    informations pertinentes telles que l'e-mail, le prénom, le nom de famille
    et le rôle.
    - `get_data` : Invite l'utilisateur à saisir les détails pour créer un
    nouvel employé, capturant l'e-mail, le mot de passe, le prénom, le nom de
    famille et le rôle.
    - `make_changes` : Tente de créer un nouvel objet `User` et un nouvel objet
    `Employee` avec les données fournies. Gère les éventuelles `IntegrityError`
    en affichant un message d'erreur et en demandant à l'utilisateur de créer à
    nouveau un employé.
    - `collect_changes` : Confirme la création d'un nouvel employé et affiche
    un message de réussite.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des employés.

    Cette classe encapsule la fonctionnalité pour créer de nouveaux employés,
    en veillant à ce que seuls les utilisateurs disposant des permissions
    appropriées puissent effectuer cette action. Elle tire parti de la classe
    `EpicEventsCommand` pour les fonctionnalités de commande communes, telles
    que l'affichage des invites de saisie et la gestion de la saisie
    utilisateur.
    """

    help = "Demande de saisir les détails pour créer un nouvel employé."
    action = "CREATE"
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
                "name": employee.get_full_name,
                "role": employee.role,
            }
            table_data[f"Employee {employee.id}"] = employee_data

        create_queryset_table(
            table_data, "Employee", headers=self.headers["employee"])

    def get_data(self):
        self.display_input_title("Enter details to create an employee:")

        return {
            "email": self.email_input("Email address"),
            "password": self.password_input("Password"),
            "first_name": self.text_input("First name"),
            "last_name": self.text_input("Last name"),
            "role": self.choice_str_input(
                ("SA", "SU", "MA"), "Role [SA]les, [SU]pport, [MA]nagement")
        }

    @transaction.atomic
    def make_changes(self, data):
        try:
            user = UserModel.objects.create_user(
                data.pop("email", None), data.pop("password", None))
            self.object = Employee.objects.create(**data, user=user)
            return self.object
        except IntegrityError:
            create_error_message("Email")
            call_command("employee_create")
            sys.exit()

    def collect_changes(self):
        self.fields = ["email", "first_name", "last_name", "role"]

        create_success_message("Employee", "created")
        self.update_table.append([f"Email: , {self.object.user.email}"])
        super().collect_changes()

    def go_back(self):
        call_command("employee")
        sys.exit()

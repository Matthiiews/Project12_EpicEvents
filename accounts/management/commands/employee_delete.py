import sys

from django.core.management import call_command
from accounts.models import Employee

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table, create_pretty_table
from cli.utils_messages import create_invalid_error_message


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour gérer les suppressions d'employés dans un système. Elle est
    spécifiquement adaptée aux utilisateurs disposant des permissions "MA", ce
    qui indique qu'elle est destinée aux gestionnaires.

    - `help` : Une chaîne décrivant l'objectif de la commande, qui consiste à
    demander les détails nécessaires pour supprimer un employé.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "DELETE".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande,
    dans ce cas, seul "MA" (Management) a la permission.

    Les principales méthodes de cette classe incluent :

    - `get_create_model_table` : Génère une table de tous les e-mails des
    employés pour aider l'utilisateur à sélectionner un employé à supprimer.
    - `get_requested_model` : Invite l'utilisateur à saisir l'adresse e-mail
    de l'employé qu'il souhaite supprimer et affiche les détails de l'employé
    pour confirmation.
    - `get_data` : Invite l'utilisateur à confirmer la suppression de
    l'employé sélectionné.
    - `make_changes` : Si l'utilisateur confirme la suppression, il procède à
    la suppression de l'employé ; sinon, il annule l'opération et revient à
    l'interface de gestion des employés.
    - `collect_changes` : Confirme la suppression de l'employé et affiche un
    message de réussite.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des employés.

    Cette classe encapsule la fonctionnalité pour supprimer des employés, en
    veillant à ce que seuls les utilisateurs disposant des permissions
    appropriées puissent effectuer cette action. Elle tire parti de la classe
    `EpicEventsCommand` pour les fonctionnalités de commande communes, telles
    que l'affichage des invites de saisie et la gestion de la saisie
    utilisateur.
    """

    help = "Demande de confirmer la suppression d'un employé."
    action = "DELETE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Employee.objects.select_related("user").only("user__email").all()
        )

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
            ["Email: ", self.object.user.email],
            ["First name: ", self.object.first_name],
            ["Last name: ", self.object.last_name],
            ["Role: ", self.object.get_role_display()],
        ]
        create_pretty_table(employee_table, "Details of the Employee:")

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {"delete": self.choice_str_input(
            ("Y", "N"), "Choice to delete [Y]es or [N]o")}

    def make_changes(self, data):
        if data["delete"] == "Y":
            self.object.user.delete()
        if data["delete"] == "N":
            self.stdout.write()
            call_command("employee")
            sys.exit()

    def go_back(self):
        call_command("employee")

from django.core.management import call_command

from accounts.models import Employee

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour répertorier tous les employés du système. Elle est accessible aux
    utilisateurs disposant des permissions "SA" (Ventes), "SU" (Support) ou
    "MA" (Management).

    - `help` : Une chaîne décrivant l'objectif de la commande, qui est de
    répertorier tous les employés.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "LIST".
    - `permissions` : Une liste des rôles autorisés à exécuter cette commande.

    Les principales méthodes de cette classe incluent :

    - `get_queryset` : Initialise le queryset pour les objets `Employee`, en
    sélectionnant les objets `User` associés à chaque employé.
    - `get_create_model_table` : Génère une table de tous les employés,
    affichant des informations pertinentes telles que l'e-mail, le nom complet
    et le rôle.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des employés.

    Cette classe encapsule la fonctionnalité pour répertorier tous les
    employés, en veillant à ce que seuls les utilisateurs disposant des
    permissions appropriées puissent effectuer cette action. Elle tire parti
    de la classe `EpicEventsCommand` pour les fonctionnalités de commande
    communes, telles que l'affichage des invites de saisie et la gestion de la
    saisie utilisateur.
    """

    help = "Répertorie tous les employés."
    action = "LIST"
    permissions = ["SA", "SU", "MA"]

    def get_queryset(self):
        self.queryset = (Employee.objects.select_related("user")
                         .only("user__email").all())

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
            table_data, "Employees", headers=self.headers["employee"])

    def go_back(self):
        call_command("employee")

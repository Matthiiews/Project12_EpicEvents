from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_menu import get_app_menu
from cli.utils_messages import create_info_message


class Command(EpicEventsCommand):
    """
    Ce script définit une classe `Command` qui hérite de `EpicEventsCommand`.
    Il fournit un menu pour les opérations concernant les contrats en fonction
    du rôle de l'utilisateur.

    - L'attribut `help` fournit une brève description de l'objectif de la
    commande.
    - L'attribut `permissions` liste les rôles ayant la permission d'exécuter
    cette commande.
    - La méthode `handle` est remplacée pour personnaliser le comportement de
    la commande en fonction du rôle de l'utilisateur et de son choix dans le
    menu de l'application.

    La méthode `handle` effectue les opérations suivantes :
    - Appelle la méthode `handle` de la superclasse pour assurer une
    initialisation correcte.
    - Récupère le choix de l'utilisateur dans le menu de l'application pour la
    section "contrat".
    - Selon le rôle de l'utilisateur (`SA`, `SU` ou `MA`), elle exécute
    différentes commandes en fonction du choix de l'utilisateur :
        - Pour les rôles `SA` et `SU` :
            - Choix 1 : Appelle la commande `contract_list_filter`.
            - Choix 2 : Appelle la commande `start`.
        - Pour les rôles `MA` :
            - Choix 1 : Appelle la commande `contract_list_filter`.
            - Choix 2 : Appelle la commande `contract_create`.
            - Choix 3 : Appelle la commande `contract_update`.
            - Choix 4 : Appelle la commande `contract_delete`.
            - Choix 5 : Appelle la commande `start`.

    Cette classe illustre l'utilisation de l'héritage et du contrôle d'accès
    basé sur les rôles dans une interface en ligne de commande, permettant une
    gestion flexible et sécurisée des opérations client.
    """
    help = "Menu pour toutes les opérations concernant les contrats."
    permissions = ["SA", "SU", "MA"]

    def handle(self, *args, **options):
        super().handle(*args, **options)

        choice = get_app_menu("contract", self.user)

        if self.user.employee_users.role == "SA":
            if choice == 1:
                call_command("contract_list_filter")
            elif choice == 2:
                call_command("start")
            elif choice == 3:
                self.logout()
                create_info_message("Login out")
                call_command("start")
                return
            elif choice == 4:
                create_info_message("Living app")
                return

        if self.user.employee_users.role == "SU":
            if choice == 1:
                call_command("contract_list_filter")
            elif choice == 2:
                call_command("start")
            elif choice == 3:
                self.logout()
                create_info_message("Login out")
                call_command("start")
                return
            elif choice == 4:
                create_info_message("Living app")
                return

        if self.user.employee_users.role == "MA":
            if choice == 1:
                call_command("contract_list_filter")
            elif choice == 2:
                call_command("contract_create")
            elif choice == 3:
                call_command("contract_update")
            elif choice == 4:
                call_command("contract_delete")
            elif choice == 5:
                call_command("start")
            elif choice == 6:
                self.logout()
                create_info_message("Login out")
                call_command("start")
                return
            elif choice == 7:
                create_info_message("Living app")
                return

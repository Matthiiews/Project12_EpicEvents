from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_menu import get_app_menu
from cli.utils_messages import create_info_message


class Command(EpicEventsCommand):
    """
    Ce script définit une classe `Command` qui hérite de `EpicEventsCommand`.
    Elle fournit un menu pour les opérations liées aux clients en fonction du
    rôle de l'utilisateur.

    - L'attribut `help` fournit une brève description de l'objectif de la
    commande.
    - L'attribut `permissions` liste les rôles qui ont la permission
    d'exécuter cette commande.
    - La méthode `handle` est remplacée pour personnaliser le comportement de
    la commande en fonction du rôle de l'utilisateur et de son choix dans le
    menu de l'application.

    La méthode `handle` effectue les opérations suivantes :
    - Appelle la méthode `handle` de la superclasse pour garantir une
    initialisation appropriée.
    - Récupère le choix de l'utilisateur dans le menu de l'application pour la
    section "client".
    - Selon le rôle de l'utilisateur (`SA`, `SU` ou `MA`), elle exécute
    différentes commandes en fonction du choix de l'utilisateur :
        - Pour le rôle `SA` :
            - Choix  1 : Appelle la commande `client_list_filter`.
            - Choix  2 : Appelle la commande `client_create`.
            - Choix  3 : Appelle la commande `client_update`.
            - Choix  4 : Appelle la commande `start`.
        - Pour les rôles `SU` :
            - Choix  1 : Appelle la commande `client_list_filter`.
            - Choix  2 : Appelle la commande `start`.
        - Pour les rôles `MA` :
            - Choix  1 : Appelle la commande `client_list_filter`.
            - Choix  2 : Appelle la commande `client_delete`.
            - Choix  3 : Appelle la commande `start`.

    Cette classe démontre l'utilisation de l'héritage et du contrôle d'accès
    basé sur les rôles dans une interface en ligne de commande, permettant une
    gestion flexible et sécurisée des opérations client.
    """
    help = "Menu pour toutes les opérations liées aux clients."
    permissions = ["SA", "SU", "MA"]

    def handle(self, *args, **options):
        super().handle(*args, **options)

        choice = get_app_menu("client", self.user)

        if self.user.employee_users.role == "SA":
            if choice == 1:
                call_command("client_list_filter")
            elif choice == 2:
                call_command("client_create")
            elif choice == 3:
                call_command("client_update")
            elif choice == 4:
                call_command("start")
            elif choice == 5:
                self.logout()
                create_info_message("Login out")
                return
            elif choice == 6:
                create_info_message("Living app")
                return

        if self.user.employee_users.role == "SU":
            if choice == 1:
                call_command("client_list_filter")
            elif choice == 2:
                call_command("start")
            elif choice == 3:
                self.logout()
                create_info_message("Login out")
                return
            elif choice == 4:
                create_info_message("Living app")
                return

        if self.user.employee_users.role == "MA":
            if choice == 1:
                call_command("client_list_filter")
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

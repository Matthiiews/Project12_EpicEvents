from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_menu import get_app_menu
from cli.utils_messages import create_info_message


class Command(EpicEventsCommand):
    """
    Ce script définit une classe `Command` qui hérite de `EpicEventsCommand`.
    Il fournit un menu pour les opérations liées aux événements en fonction du
    rôle de l'utilisateur.

    - L'attribut `help` fournit une brève description de l'objectif de la
    commande.
    - L'attribut `permissions` répertorie les rôles autorisés à exécuter cette
    commande.
    - La méthode `handle` est remplacée pour personnaliser le comportement de
    la commande en fonction du rôle de l'utilisateur et de son choix dans le
    menu de l'application.

    La méthode `handle` effectue les opérations suivantes :
    - Appelle la méthode `handle` de la superclasse pour garantir une
    initialisation correcte.
    - Récupère le choix de l'utilisateur dans le menu de l'application pour la
    section "événement".
    - Selon le rôle de l'utilisateur (`SA`, `SU` ou `MA`), elle exécute
    différentes commandes en fonction du choix de l'utilisateur :
        - Pour le rôle `SA` :
            - Choix 1 : Appelle la commande `event_list_filter`.
            - Choix 2 : Appelle la commande `event_create`.
            - Choix 3 : Appelle la commande `start`.
        - Pour le rôle `SU` :
            - Choix 1 : Appelle la commande `event_list_filter`.
            - Choix 2 : Appelle la commande `event_update`.
            - Choix 3 : Appelle la commande `start`.
        - Pour le rôle `MA` :
            - Choix 1 : Appelle la commande `event_list_filter`.
            - Choix 2 : Appelle la commande `event_update`.
            - Choix 3 : Appelle la commande `event_delete`.
            - Choix 4 : Appelle la commande `start`.

    Cette classe illustre l'utilisation de l'héritage et du contrôle d'accès
    basé sur les rôles dans une interface en ligne de commande, permettant une
    gestion flexible et sécurisée des opérations sur les événements.
    """

    help = "Menu pour toutes les opérations liées aux événements."
    permissions = ["SA", "SU", "MA"]

    def handle(self, *args, **options):
        super().handle(*args, **options)

        choice = get_app_menu("event", self.user)

        if self.user.employee_users.role == "SA":
            if choice == 1:
                call_command("event_list_filter")
            elif choice == 2:
                call_command("event_create")
            elif choice == 3:
                call_command("start")
            elif choice == 4:
                self.logout()
                create_info_message("Login out")
                call_command("start")
                return
            elif choice == 5:
                create_info_message("Living app")
                return

        if self.user.employee_users.role == "SU":
            if choice == 1:
                call_command("event_list_filter")
            elif choice == 2:
                call_command("event_update")
            elif choice == 3:
                call_command("start")
            elif choice == 4:
                self.logout()
                create_info_message("Login out")
                call_command("start")
                return
            elif choice == 5:
                create_info_message("Living app")
                return

        if self.user.employee_users.role == "MA":
            if choice == 1:
                call_command("event_list_filter")
            elif choice == 2:
                call_command("event_update")
            elif choice == 3:
                call_command("start")
            elif choice == 4:
                self.logout()
                create_info_message("Login out")
                call_command("start")
                return
            elif choice == 5:
                create_info_message("Living app")
                return

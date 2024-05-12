from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_menu import get_start_menu
from cli.utils_messages import (
    create_info_message, create_permission_denied_message)


class Command(EpicEventsCommand):
    """
    Ce script définit une classe `Command` qui hérite de `EpicEventsCommand`.
    Il fournit le menu de démarrage pour choisir le modèle vers lequel aller
    ensuite.

    - L'attribut `help` fournit une brève description du but de la commande.
    - L'attribut `permissions` répertorie les rôles autorisés à exécuter cette
    commande.
    - La méthode `handle` est remplacée pour personnaliser le comportement de
    la commande en fonction du rôle de l'utilisateur et de son choix dans le
    menu de l'application.

    La méthode `handle` effectue les opérations suivantes :
    - Appelle la méthode `handle` de la superclasse pour assurer une
    initialisation correcte.
    - Récupère le choix de l'utilisateur dans le menu de démarrage de
    l'application pour l'étape suivante.

    Cette classe illustre l'utilisation de l'héritage et du contrôle d'accès
    basé sur les rôles dans une interface en ligne de commande, permettant une
    gestion flexible et sécurisée.
    """

    help = "Start the Epic Events program."
    permissions = ["SA", "SU", "MA"]

    def handle(self, *args, **options):
        """
        Gère l'exécution de la commande.

        Affiche le menu de démarrage et gère l'entrée de l'utilisateur pour
        naviguer vers différentes sections du programme Epic Events.
        """
        super().handle(*args, **options)

        choice = get_start_menu("Epic Events")

        if choice == 1:
            if self.user.employee_users.role in ["SA", "SU"]:
                create_permission_denied_message
                call_command("start")
            elif self.user.employee_users.role == "MA":
                call_command("employee")
        elif choice == 2:
            call_command("client")
        elif choice == 3:
            call_command("contract")
        elif choice == 4:
            call_command("event")
        elif choice == 5:
            return
        elif choice == 6:
            self.logout()
            create_info_message("logging out...")
            call_command("start")
            return

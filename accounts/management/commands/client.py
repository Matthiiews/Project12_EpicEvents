from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_menu import get_app_menu
from cli.utils_messages import create_info_message


class Command(EpicEventsCommand):
    """
    This script defines a class `Command` that inherits from
    `EpicEventsCommand`. It provides a
    menu for operations around clients based on the user's role.
    """
    help = "Menu for all operations around the clients."
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
                call_command("client_delete")
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

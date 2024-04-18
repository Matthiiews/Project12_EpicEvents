from django.core.management import call_command

from cli.utils_custom_command import EpicEventsCommand
from cli.utils_menu import get_app_menu


class Command(EpicEventsCommand):
    """
    This script defines a class `Command` that inherits from
    `EpicEventsCommand`. It provides a menu for operations around events based
    on the user's role.
    """

    help = "Menu for all operations around the events."
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

        if self.user.employee_users.role == "SU":
            if choice == 1:
                call_command("event_list_filter")
            elif choice == 2:
                call_command("event_update")
            elif choice == 3:
                call_command("start")

        if self.user.employee_users.role == "MA":
            if choice == 1:
                call_command("event_list_filter")
            elif choice == 2:
                call_command("event_update")
            elif choice == 3:
                call_command("event_delete")
            elif choice == 4:
                call_command("start")

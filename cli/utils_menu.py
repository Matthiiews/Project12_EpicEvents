BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BOLD = "\033[1m"
UNDERLINE = "\033[4m"

ENDC = "\033[0m"  # to reset the style coded before


def style_text_display(text, color=ENDC, bold=False, underline=False,
                       end="\n"):
    """
    Styles the provided text with the specified color
    and/or boldness and/or underlines and prints it.

    Args:
        text (str): The text to be styled and displayed.
        color (str, optional): The color to apply to the text.
        Defaults to None.
        bold (bool, optional): Whether to apply bold formatting to the text.
        Defaults to False.
        underline (bool, optional): To underline the text. Defaults to False.
        end (str, optional): Defines the spaces or non-spaces for the
        print-statement. Default is linebreak. "\n".
    """
    style = f"{color}"
    if bold:
        style += f"{BOLD}"
    if underline:
        style += f"{UNDERLINE}"
    print(f"{style}{text}{ENDC}", end=end)  # reset the color


def _display_menu_headline(text):
    """
    PRIVATE FUNCTION, which styles the headline of the main menu.

    Args:
        text (str): The text will be the headline of the main menu.
    """
    style_text_display(f"{'':^2}** {text} **{'':^2}", color=MAGENTA, bold=True,
                       underline=True, end="\n\n")


def _display_menu_title(text):
    """
    PRIVATE FUNCTION, which styles the title of the menu.

    Args:
        text (str): The text will be the title of the menu.
    """
    style_text_display(f"{'':^3}*** {text} ***{'':^3}", color=CYAN, bold=True)


def _display_choices(option, text, color=BLUE):
    """
    PRIVATE FUNCTION, display the possible choices with information to choose
    in menu.
        exm: [1] Manage the employees ([option] text)
    Args:
        option (int): Int-value which is defined in the menu-function,
        beginning from 0. exp: [1].
        text (str): After the option value, there is a text as information,
        to choose.
        color (str, optional): The color of the option can be set.
        Default is Blue.
    """
    style_text_display(f"{'':^4}[{option}] ", color=color, bold=True, end="")
    style_text_display(f"{text}", bold=True)


def display_new_line():
    """
    Display a new line
    """
    print()


def _create_start_menu_choices(menu_choices):
    """
    creates the menu choices for the start menu.
    Args:
        menu_choices (dict): contains the choices the user has.
    """
    for key, choice_desc in menu_choices.items():
        if isinstance(choice_desc, list) and len(choice_desc) == 2:
            choice_key, choice_text = choice_desc
            _display_choices(key, choice_text, color=RED)
        else:
            _display_choices(key, f"Manage the {choice_desc}")
    display_new_line()


def _create_menu_choices(menu_choices, app):
    """
    creates the menu choices.
    Args:
        menu_choices (dict): contains the choices the user has.
        app (str): to determine to display the choices in a different manner.
    """
    for key, choice_desc in menu_choices.items():
        if isinstance(choice_desc, list) and len(choice_desc) == 2:
            choice_key, choice_text = choice_desc
            _display_choices(key, choice_text, color=RED)
        else:
            _display_choices(key, f"{choice_desc} {app}")
    display_new_line()


def get_start_menu(title):
    """
    Displays the start menu and prompts the user for input.

    Args:
        title (str): The title of the menu.

    Returns:
        int: The user's choice.

    Raises:
        ValueError: If the user enters a choice that is not an integer or not
        in the available choices.
    """
    possible_choices = {
        1: "employees",
        2: "clients",
        3: "contracts",
        4: "events",
        5: ["quit", "Quit program"],
        6: ["logout", "Logout"],
    }

    _display_menu_headline(f"Welcome to {title}")
    _display_menu_title(f"{title} Menu")

    _create_start_menu_choices(possible_choices)

    while True:
        try:
            choice = int(input(" Please enter your choice: "))
            print()
            break
        except ValueError:
            print("  Invalid input. Please enter a number.", end="\n\n")
    return choice


def get_app_menu(app, user):
    """
    Displays the menu and prompts the user for input.

    Args:
        app (str): The title of the menu.
        user (user instance): To determine what menu to display.

    Returns:
        int: The user's choice.

    Raises:
        ValueError: If the user enters a choice that is not an integer or not
        in the available choices.
    """
    choices_by_role_and_app = {
        "SA": {
            "employee": {1: "List", 2: ["quit", "Go back to Main Menu"]},
            "client": {
                1: "List and filter",
                2: "Create",
                3: "Update",
                4: ["quit", "Go back to Main Menu"],
            },  # filter possible
            "contract": {
                1: "List and filter",
                2: ["quit", "Go back to Main Menu"],
            },  # filter possible because MA creates the contract with
            # employee of client
            "event": {
                1: "List and filter",
                2: "Create",
                3: ["quit", "Go back to Main Menu"],
            },  # filter possible because employee created the client, is
            # associated with contract
        },
        "SU": {
            "employee": {1: "List", 2: ["quit", "Go back to Main Menu"]},
            "client": {
                1: "List and filter", 2: ["quit", "Go back to Main Menu"]},
            "contract": {
                1: "List and filter", 2: ["quit", "Go back to Main Menu"]},
            "event": {
                1: "List and filter",
                2: "Update",
                3: ["quit", "Go back to Main Menu"],
            },
        },
        "MA": {
            "employee": {
                1: "List",
                2: "Create",
                3: "Update",
                4: "Delete",
                5: ["quit", "Go back to Main Menu"],
            },  # can filter employees, create filter logic inside List
            "client": {
                1: "List and filter",
                2: "Delete",
                3: ["quit", "Go back to Main Menu"],
            },
            "contract": {
                1: "List and filter",
                2: "Create",
                3: "Update",
                4: "Delete",
                5: ["quit", "Go back to Main Menu"],
            },  # can filter contracts, but user_queryset not useful because
            # SA employee
            "event": {
                1: "List and filter",
                2: "Update",
                3: "Delete",
                4: ["quit", "Go back to Main Menu"],
            },
        },
    }

    # Retrieve the possible choices for the given role and app
    possible_choices = choices_by_role_and_app.get(
        user.employee_users.role, {}).get(app, {})

    app_capitalized = app.title()

    _display_menu_headline(f"Menu of the {app_capitalized}s")
    _display_menu_title(f"{app_capitalized} Menu")
    _create_menu_choices(possible_choices, app)

    while True:
        try:
            choice = int(input("Please enter your choice: "))
            print()
            break
        except ValueError:
            print("  Invalid input. Please enter a number.", end="\n\n")
    return choice

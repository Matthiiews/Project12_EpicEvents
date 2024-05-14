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
    Stylise le texte fourni avec la couleur spécifiée et/ou en gras et/ou
    souligné et l'affiche.

    Args:
        text (str): Le texte à styliser et afficher.
        color (str, optionnel): La couleur à appliquer au texte. Par défaut,
        None.
        bold (bool, optionnel): Indique si le texte doit être en gras. Par
        défaut, False.
        underline (bool, optionnel): Indique si le texte doit être souligné.
        Par défaut, False.
        end (str, optionnel): Définit les espaces ou les non-espaces pour
        l'instruction d'impression. Par défaut, saut de ligne.
    """
    style = f"{color}"
    if bold:
        style += f"{BOLD}"
    if underline:
        style += f"{UNDERLINE}"
    print(f"{style}{text}{ENDC}", end=end)  # réinitialise la couleur


def _display_menu_headline(text):
    """
    FONCTION PRIVÉE, qui stylise le titre du menu principal.

    Args :
        text (str): Le texte sera le titre du menu principal.
    """
    style_text_display(f"{'':^2}** {text} **{'':^2}", color=MAGENTA, bold=True,
                       underline=True, end="\n\n")


def _display_menu_title(text):
    """
    FONCTION PRIVÉE, qui stylise le titre du menu.

    Args :
        text (str): Le texte sera le titre du menu.
    """
    style_text_display(f"{'':^3}*** {text} ***{'':^3}", color=CYAN, bold=True)


def _display_choices(option, text, color=BLUE):
    """
    FONCTION PRIVÉE, affiche les choix possibles avec des informations pour
    choisir dans le menu.
    ex. : [1] Gérer les employés ([option] texte)

    Args :
        option (int) : Valeur entière définie dans la fonction de menu,
        commençant à partir de 0. exp : [1].
        text (str) : Après la valeur de l'option, il y a un texte en tant
        qu'information, pour choisir.
        color (str, facultatif) : La couleur de l'option peut être définie.
        Par défaut, c'est le bleu.
    """
    style_text_display(f"{'':^4}[{option}] ", color=color, bold=True, end="")
    style_text_display(f"{text}", bold=True)


def display_new_line():
    """
    Affiche une nouvelle ligne.
    """
    print()


def _create_start_menu_choices(menu_choices):
    """
    Crée les options de menu pour le menu de démarrage.
    Args :
        menu_choices (dict) : contient les choix disponibles pour
        l'utilisateur.
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
    Crée les choix de menu.
    Args :
        menu_choices (dict) : contient les choix disponibles pour
        l'utilisateur.
        app (str) : pour déterminer l'affichage des choix de manière
        différente.
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
    Affiche le menu de démarrage et invite l'utilisateur à saisir une entrée.
    Args :
        title (str) : Le titre du menu.

    Returns :
        int : Le choix de l'utilisateur.

    Raises :
        ValueError : Si l'utilisateur entre un choix qui n'est pas un entier
        ou qui n'est pas parmi les choix disponibles.
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
    Affiche le menu et invite l'utilisateur à saisir une entrée.
    Args :
        app (str) : Le titre du menu.
        user (instance d'utilisateur) : Pour déterminer quel menu afficher.

    Returns :
        int : Le choix de l'utilisateur.

    Raises :
        ValueError : Si l'utilisateur entre un choix qui n'est pas un entier
        ou qui n'est pas parmi les choix disponibles.
    """
    choices_by_role_and_app = {
        "SA": {
            "employee": {
                1: "List",
                2: ["quit", "Go back to Main Menu"]},
            "client": {
                1: "List and filter",
                2: "Create",
                3: "Update",
                4: ["quit", "Go back to Main Menu"],
                5: ["Logout", "logout"],
                6: ["quit", "Quit program"]
            },  # Filtre possible.
            "contract": {
                1: "List and filter",
                2: ["quit", "Go back to Main Menu"],
                3: ["Logout", "logout"],
                4: ["quit", "Quit program"]
            },  # Filtre possible car le MA crée le contrat avec l'employé du
                # client.
            "event": {
                1: "List and filter",
                2: "Create",
                3: ["quit", "Go back to Main Menu"],
                4: ["Logout", "logout"],
                5: ["quit", "Quit program"]
            },  # Filtrer possible car l'employé a créé le client, est associé
            # au contrat.
        },
        "SU": {
            "employee": {
                1: "List",
                2: ["quit", "Go back to Main Menu"],
                3: ["Logout", "logout"],
                4: ["quit", "Quit program"]
                },
            "client": {
                1: "List and filter",
                2: ["quit", "Go back to Main Menu"],
                3: ["Logout", "logout"],
                4: ["quit", "Quit program"]
                },
            "contract": {
                1: "List and filter",
                2: ["quit", "Go back to Main Menu"],
                3: ["Logout", "logout"],
                4: ["quit", "Quit program"]
                },
            "event": {
                1: "List and filter",
                2: "Update",
                3: ["quit", "Go back to Main Menu"],
                4: ["Logout", "logout"],
                5: ["quit", "Quit program"]
            },
        },
        "MA": {
            "employee": {
                1: "List",
                2: "Create",
                3: "Update",
                4: "Delete",
                5: ["quit", "Go back to Main Menu"],
                6: ["Logout", "logout"],
                7: ["quit", "Quit program"]

            },  # Peut filtrer les employés, créer une logique de filtre à
            # l'intérieur de la Liste.
            "client": {
                1: "List and filter",
                2: "Delete",
                3: ["quit", "Go back to Main Menu"],
                4: ["Logout", "logout"],
                5: ["quit", "Quit program"]
            },
            "contract": {
                1: "List and filter",
                2: "Create",
                3: "Update",
                4: "Delete",
                5: ["quit", "Go back to Main Menu"],
                6: ["Logout", "logout"],
                7: ["quit", "Quit program"]
            },  # Peut filtrer les contrats, mais user_queryset n'est pas
            # utile parce que l'employé SA.
            "event": {
                1: "List and filter",
                2: "Update",
                3: "Delete",
                4: ["quit", "Go back to Main Menu"],
                5: ["Logout", "logout"],
                6: ["quit", "Quit program"]
            },
        },
    }

    # Récupérer les choix possibles pour le rôle et l'application donné.
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

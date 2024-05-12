from cli.utils_menu import style_text_display, YELLOW, RED, GREEN


def create_success_message(text, action):
    """
    Affiche un message de réussite.
    Args:
        text (str): Le texte spécifie quel modèle.
        action (str): L'action spécifie ce qui a été réussi.
    """
    print()
    style_text_display(f" {text} successfully {action}!", color=YELLOW)
    print()


def create_error_message(text):
    """
    Affiche un message d'erreur, lorsque quelque chose existe déjà.
    Args:
        text (str): Le texte spécifie ce qui existe déjà.
    """
    print()
    style_text_display(f"{'':^2}{text} already exists !", color=RED, bold=True)
    print()


def create_invalid_error_message(text):
    """
    Affiche un message d'erreur.
    Args:
        text (str): Le texte spécifie ce qui est invalide.
    """
    print()
    style_text_display(f"{'':^2} Invalid {text} !", color=RED, bold=True)
    print()


def create_token_error_message(text):
    """
    Affiche un message indiquant qu'il y a un problème avec le jeton.
    Args:
        text (str): Le texte est le message.
    """
    print()
    style_text_display(f"{'':^2} {text}", color=RED, bold=True)
    print()


def create_does_not_exists_message(text):
    """
    Affiche un message indiquant que quelque chose n'existe pas.
    Args:
        text (str): Le texte précisera ce qui n'existe pas.
    """
    print()
    style_text_display(
        f"{'':^2} {text} does not exists !", color=RED, bold=True)
    print()


def create_permission_denied_message():
    """Affiche un message de refus de permission."""
    print()
    style_text_display(f"{'':^2} Permission denied !", color=RED, bold=True)
    print()


def create_info_message(text):
    """
    Affiche un message d'information donné.
    Args:
        text (str): Le contenu du message d'information.
    """
    print()
    style_text_display(f"{'':^2}{text}", color=GREEN, bold=True)
    print()

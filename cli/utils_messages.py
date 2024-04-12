from cli.utils_menu import style_text_display, YELLOW, RED, GREEN


def create_success_message(text, action):
    """
    Displays a success message.
    Args:
        text (str): The text will specify what model.
        action (str): The action specifies what was successfully done.
    """
    print()
    style_text_display(f" {text} successfully {action}!", color=YELLOW)
    print()


def create_error_message(text):
    """
    Displays an error message, when something already exists.
    Args:
        text (str): The text will specify what already exists.
    """
    print()
    style_text_display(f"{'':^2}{text} already exists !", color=RED, bold=True)
    print()


def create_invalid_error_message(text):
    """
    Displays an invalid message.
    Args:
        text (str): The text will specify what is invalid.
    """
    print()
    style_text_display(f"{'':^2} Invalid {text} !", color=RED, bold=True)
    print()


def create_token_error_message(text):
    """
    Displays a message that there is a problem with the token.
    Args:
        text (str): The text is the message.
    """
    print()
    style_text_display(f"{'':^2} {text}", color=RED, bold=True)
    print()


def create_does_not_exists_message(text):
    """
    Displays a does not exist message.
    Args:
        text (str): The text will specify what does not exist.
    """
    print()
    style_text_display(
        f"{'':^2} {text} does not exists !", color=RED, bold=True)
    print()


def create_permission_denied_message():
    """Displays a permission denied message."""
    print()
    style_text_display(f"{'':^2} Permission denied !", color=RED, bold=True)
    print()


def create_info_message(text):
    """
    Displays any given informational message.
    Args:
        text (str): The content of the informational message.
    """
    print()
    style_text_display(f"{'':^2}{text}", color=GREEN, bold=True)
    print()

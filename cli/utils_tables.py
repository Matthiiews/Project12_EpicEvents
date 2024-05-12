from tabulate import tabulate

from cli.utils_menu import display_new_line, style_text_display, CYAN, WHITE
from cli.utils_messages import create_info_message


def display_table_title(text):
    """
    Affiche le titre du tableau avec le style spécifié.

    Args :
        text (str): Le texte du titre à afficher.
    """
    if text is None or text.strip() == "":
        raise ValueError("Title text cannot be empty or None")

    styled_text = f"{'':^3}{text} {'':^3}"  # Centre le texte avec un remplissage.
    style_text_display(styled_text, color=CYAN, bold=True)


def display_info(order_by_fields):
    """
    Affiche les informations du filtrage du 'user_queryset'.

    Args :
        order_by_fields (str) : Les 'order_by_fields' à afficher.
    """
    if order_by_fields is None:
        raise ValueError("Info cannot be None")

    # ['email', 'first_name']
    # ['-email', '-first_name']
    ordering_info = []
    for item in order_by_fields:
        if item.startswith("-"):
            field = item[1:]
            ordering_info.append(f"descending {field}")
        else:
            ordering_info.append(f"ascending {item}")

    styled_text = f"{'':^3}{ordering_info} {'':^3}"
    style_text_display(styled_text, color=WHITE)


def create_pretty_table(table_list, title=None, headers=None,
                        order_by_fields=None):
    """
    Crée un tableau formaté en utilisant la bibliothèque tabulate.

    Args:
        table_list (list): Liste de listes représentant les lignes du tableau.
        title (str, facultatif): Titre à afficher au-dessus du tableau. Par
        défaut, None.
        headers (list, facultatif): Liste de chaînes représentant les en-têtes
        de colonnes. Par défaut, None.
        order_by_fields (list, facultatif): Uniquement pour list_filter. Pour
        afficher les informations du filtre. Par défaut, None.
    """
    if not table_list:
        print("No data available to create table.")
        return

    if title:
        display_table_title(title)

    if order_by_fields:
        display_info(order_by_fields)

    table_format = "pretty"
    if headers is not None:
        table = tabulate(table_list, headers=headers, tablefmt=table_format)
    else:
        table = tabulate(table_list, tablefmt=table_format)

    indented_table = "\n".join("   " + line for line in table.split("\n"))
    print(indented_table)
    display_new_line()


def create_model_table(model, column_label, title):
    """
    Crée des données pour la fonction create_pretty_table basée sur un modèle.

    Args:
        model (Modèle): Classe de modèle Django.
        column_label (str): Étiquette de la colonne à afficher.
        title (str): Titre pour le tableau.
    """

    all_items = model.objects.all()
    all_items_list = []

    if all_items:
        for item in all_items:
            if "." in column_label:
                # Gérer les attributs imbriqués
                attribute_chain = column_label.split(".")
                attribute_value = item
                for attr in attribute_chain:
                    attribute_value = getattr(attribute_value, attr)
                column_title = attribute_chain[-1].title()
            else:
                attribute_value = getattr(item, column_label)
                column_title = column_label.title()

            all_items_table = [column_title + ": ", attribute_value]
            all_items_list.append(all_items_table)

        create_pretty_table(all_items_list, f"All {title}: ")
    else:
        create_info_message(f"No table available, until now !")


def create_queryset_table(queryset, title, label=None, headers=None,
                          order_by_fields=None):
    """
    Crée un tableau formaté basé sur le queryset fourni, le titre, l'étiquette
    et les en-têtes.

    Args:
        queryset: Un QuerySet Django représentant les données à afficher dans
        le tableau.
        title (str): Le titre du tableau.
        label (str, facultatif): Une étiquette à préfixer à chaque ligne du
        tableau. Par défaut, None.
        headers (list, facultatif): Une liste d'en-têtes de colonnes pour le
        tableau. Si fourni, chaque ligne dans le tableau sera étiquetée avec
        ces en-têtes. Par défaut, None.
        order_by_fields (list, facultatif): Uniquement pour list_filter. Pour
        afficher les informations du filtre.

    Returns:
        None: La fonction ne retourne pas de valeur. Au lieu de cela, elle
        imprime le tableau formaté.

    Remarque:
        La fonction formate le tableau en fonction du queryset, du titre, de
        l'étiquette et des en-têtes fournis.
        Si à la fois l'étiquette et les en-têtes sont fournis, chaque ligne
        sera étiquetée avec l'étiquette, et le tableau aura les en-têtes
        spécifiés. Si seule l'étiquette est fournie, chaque ligne sera
        étiquetée avec l'étiquette. Si seuls les en-têtes sont fournis,
        le tableau aura les en-têtes spécifiés.
        Si ni l'étiquette ni les en-têtes ne sont fournis, le tableau
        affichera directement le queryset.

        Cette fonction suppose que la fonction `create_pretty_table` est
        définie ailleurs pour gérer le formatage réel du tableau.
    """
    if not queryset:
        create_info_message("No data available")
        return

    all_items_list = []

    if label is not None:
        for item in queryset.values():
            item_table = [label + ": ", item]
            all_items_list.append(item_table)

        create_pretty_table(all_items_list, f"All {title}: ",
                            order_by_fields=order_by_fields)

    if headers is not None:
        for key, values in queryset.items():
            item_table = [f"{key}: "]
            for value in values.values():
                item_table.append(value)
            all_items_list.append(item_table)

        create_pretty_table(
            all_items_list, headers=headers, title=f"All {title}: ",
            order_by_fields=order_by_fields)

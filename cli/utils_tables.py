from tabulate import tabulate

from cli.utils_menu import display_new_line, style_text_display, CYAN, WHITE
from cli.utils_messages import create_info_message


def display_table_title(text):
    """
    Prints the title of the table with specified styling.

    Args:
        text (str): The title text to be displayed.
    """
    if text is None or text.strip() == "":
        raise ValueError("Title text cannot be empty or None")

    styled_text = f"{'':^3}{text} {'':^3}"  # Center-align the text with padding
    style_text_display(styled_text, color=CYAN, bold=True)


def display_info(order_by_fields):
    """
    Prints information of the filtering of the 'user_queryset'.

    Args:
        order_by_fields (str): The 'order_by_fields' to be displayed.
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
    Creates a formatted table using the tabulate library.

    Args:
        table_list (list): List of lists representing the rows of the table.
        title (str, optional): Title to display above the table
        . Defaults to None.
        headers (list, optional): List of strings representing column headers.
        Defaults to None.
        order_by_fields (list, optional): Just for list_filter. To display
        info of the filter.
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
    Creates data for the create_pretty_table function based on a model.

    Args:
        model (Model): Django model class.
        column_label (str): Label of the column to display.
        title (str): Title for the table.
    """

    all_items = model.objects.all()
    all_items_list = []

    if all_items:
        for item in all_items:
            if "." in column_label:
                # Handle nested attributes
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
    Creates a formatted table based on the provided queryset, title, label,
    and headers.
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

            create_model_table(all_items_list, headers=headers,
                               title=f"All {title}: ",
                               order_by_fields=order_by_fields)

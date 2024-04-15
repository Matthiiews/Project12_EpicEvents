import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, call_command
from django.core.validators import validate_email
from django.utils.timezone import make_aware

from cli.utils_menu import BOLD, ENDC, style_text_display, BLUE
from cli.utils_messages import (
    create_invalid_error_message,
    create_permission_denied_message,
    create_info_message,
)
from cli.utils_tables import create_pretty_table
from cli.utils_token_mixin import JWTTokenMixin


class EpicEventsCommand(JWTTokenMixin, BaseCommand):
    """
    Custom management command for handling epic events.

    Class attributes:
        action (str): The action to perform (LIST, CREATE, UPDATE, DELETE).
        permissions (str): The role required to access the command.

    Instance attributes:
        object (Any): The object to be manipulated by the command.
        queryset (Any): The queryset is used only in "action = 'LIST'" and
        requests the queryset of
            a model.
        fields (list): A list of fields to update.
        fields_to_update (list): A list of fields that need to be updated.
        available_fields (dict): A dictionary of available fields.
        update_table (list): A list representing the update table.

    Methods:
        __init__(self, *args, **options): Initializes the command with options.
        handle(self): The main method to execute the command's action.

    Note:
        - Ensure the `action` attribute is set to one of 'LIST', 'CREATE',
        'UPDATE', 'DELETE'.
        - The `permissions` attribute should be set to the role required to
        execute the command.

    """

    help = "Custom BaseCommand for handling epic events"
    action = None
    permissions = None

    def __init__(self, *args, **options):
        """
        Initialize the subclass attributes.
        """
        super().__init__(*args, **options)
        self.available_fields = dict()
        self.client = None
        self.employee = None
        self.fields = list()
        self.fields_to_update = list()
        self.headers = list()
        self.object = None
        self.queryset = None
        self.update_table = list()

    @classmethod
    def custom_input(cls, label):
        value = input(label)

        if value in ["", " "]:
            print()
            call_command("start")
            sys.exit()

        return value

    @classmethod
    def text_input(cls, label, required=True):
        """
        Prompts the user for text/string input and handles required fields.

        This method displays a prompt to the user with a given label and
        optionally marks the field as required. If the field is marked as
        required, the method ensures that the user provides a non-empty
        input. If the user does not provide an input or enters only whitespace,
        the method calls 'start' command and prints a blank line. If the
        field is not required or the user provides a valid input, the method
        returns the input value.

        Args:
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            str: The user's input as a string.

        Raises:
            ValueError: If the input is required but not provided.
        """
        original_label = label

        if required:
            label = f"{label}*"
        label = f"{'':^5}{BOLD}{label}{ENDC}: "

        value = cls.custom_input(label)
        if not value and required:
            create_invalid_error_message("input")
            value = cls.text_input(original_label, required=required)

        return value

    @classmethod
    def int_input(cls, label, required=True):
        """
        Prompts the user for number/int input and handles required fields.
        Exit of function
        possible with '' or ' '.

        Args:
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            int: The user's input as an int.

        Notes:
            uses a ValueError if the input of user is '', the 'start'-command
            will be called to
            exit the function.
        """
        original_label = label

        if required:
            label = f"{label}*"
        label = f"{'':^5}{BOLD}{label}{ENDC}: "

        try:
            value = int(cls.custom_input(label))
        except ValueError:
            print("Invalid input! Number input.")
            value = cls.int_input(original_label, required=required)

        return value

    @classmethod
    def decimal_input(cls, label, required=True):
        """
        Prompts the user for decimal/float input and handles required fields.

        Args:
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            float: The user's input as a decimal/float.

        Raises:
            InvalidOperation: If the input is other than decimal.
        """
        original_label = label

        if required:
            label = f"{label}*"
        label = f"{'':^5}{BOLD}{label}{ENDC}: "

        value = cls.custom_input(label)

        try:
            value = Decimal(value)
        except InvalidOperation:
            print("Invalid input! Decimal input.")
            value = cls.decimal_input(original_label, required=required)

        return value

    @classmethod
    def choice_str_input(cls, options, label, required=True):
        """
        Prompts the user for one choice string input and handles required
        fields.

        Args:
            options (tuple): The options are the possible choices the user can
            make.
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            str: The user's input as a string.

        Notes:
            If the user enters '' or ' ' the program calls the 'start'-command
            to exit.
        """
        value = cls.text_input(label, required)

        if value not in options:
            value = cls.choice_str_input(options, label, required)

        return value

    @classmethod
    def choice_int_input(cls, options, label, required=True):
        """
        Prompts the user for one choice int input and handles required fields.

        Args:
            options (tuple): The options are the possible choices the user can
            make.
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            int: The user's input as an int.

        Notes:
            If the user enters '' or ' ' the program calls the 'start'-command
            to exit.
        """
        value = cls.int_input(label, required)

        if value not in options:
            value = cls.choice_int_input(options, label, required)
        if value in ["", " "]:
            print()
            call_command("start")
            sys.exit()

        return value

    @classmethod
    def multiple_choice_str_input(cls, options, label, required=True):
        """
        Prompts the user for one or many choice(s) as string input(s) and
        handles required fields.

        Args:
            options (tuple): The options are the possible choices the user can
            make.
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            list: The user's input as a list.

        Notes:
            If the user enters '' or ' ' the program calls the 'start'-command
            to exit.
        """
        values = cls.text_input(label, required)

        return [w for w in values if w in options]

    @classmethod
    def date_input(cls, label, required=True):
        """
        Prompts the user for a date input in format: DD/MM/YYYY and handles
        required fields.

        Args:
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            date: The user's input as a date object.

        Notes:
            If the user enters '' or ' ' the program calls the 'start'-command
            to exit.
        """
        value = cls.text_input(label, required)  # DD/MM/YYYY

        try:
            # save the given date in format: 2025-12-15 00:00:00
            value = datetime.strptime(value, "%d/%m/%Y")
            # Make the datetime object timezone-aware
            value = make_aware(value)
        except ValueError:
            value = cls.date_input(label, required)

        return value

    @classmethod
    def email_input(cls, label, required=True):
        """
        Prompts the user for a valid email input and handles required fields.
        The build-in function
        'validate_email' checks if the email input is a valid email address.

        Args:
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            email: The user's input as an email.

        Raises:
            ValidationError: Uses the ValidationError to recall the function
            again if the email
            address is wrong.

        Notes:
            If the user enters '' or ' ' the program calls the 'start'-command
            to exit.
        """
        value = cls.text_input(label, required)

        try:
            validate_email(value)
        except ValidationError:
            value = cls.email_input(label, required)

        return value

    @classmethod
    def password_input(cls, label, required=True):
        """
        Prompts the user for a valid password input and handles required
        fields. The build-in
        function 'validate_password' checks if the password input fits the
        'settings.AUTH_PASSWORD_VALIDATORS'

        Args:
            label (str): The label to display next to the input prompt.
            required (bool, optional): Whether the input field is required.
            Defaults to True.

        Returns:
            password: The user's input as a password.

        Raises:
            ValidationError: Uses the ValidationError to recall the function
            again if the password
            does not fit the 'settings.AUTH_PASSWORD_VALIDATORS' criteria and
            prints the error
            message, why the password is not valid.

        Notes:
            If the user enters '' or ' ' the program calls the 'start'-command
            to exit.
        """
        value = cls.text_input(label, required)
        # value = maskpass.askpass(prompt=label, mask="*") if required else
        # input(label)

        try:
            validate_password(value)
        except ValidationError as e:
            print(f"{'':^4}", e.messages)
            value = cls.password_input(label, required)

        return value

    @classmethod
    def display_input_title(cls, text):
        """
        Display a title above the input.

        Args:
             text (str): The text is the printed title above the input.
        """
        style_text_display(f"{'':^3}{text} {'':^3}", color=BLUE, bold=True)

    def display_new_line(self):
        """Prints a new line"""
        print()

    # METHODS FOR ALL ACTIONS: (LIST, LIST_FILTER, CREATE, UPDATE AND DELETE):
    def get_instance_data(self):
        """
        Within this method, create a table of the existing model instances.
        """
        self.headers = {
            "employee": ["", "** Employee email **" "", "Name", "Role"],
            "client": [
                "",
                "** Client email **",
                "Name",
                "Phone",
                "Company name",
                "Employee",
            ],
            "contract": [
                "",
                "** Client email **",
                "Total amount",
                "Amount paid",
                "Rest amount",
                "State",
                "Employee",
            ],
            "event": [
                "",
                "** Client email **",
                "Date",
                "Name",
                "Location",
                "Max guests",
                "Employee",
            ],
        }
        pass

    # METHODS FOR ACTIONS: (LIST_FILTER, CREATE, UPDATE AND DELETE):
    def get_data(self):
        """
        Prompts the user for data/information.

        Returns:
            dict: Gets the user's input and is stored in a dictionary.
        """
        return dict()

    def go_back(self):
        """Calls another Command."""
        pass

    # METHODS FOR ACTIONS: CREATE, UPDATE AND DELETE:
    def make_changes(self, data):
        """
        Verifies if the user's input from 'get_data' exists. Makes queries to
        verify the user's
        input from the database. Makes the changes: 'create', 'update' or
        'delete'.

        Args:
             data (dict): Contains the user's input from 'get_data' function.

        Errors:
            Throws different error messages, which are defined in
            'cli/utils_messages.py'.
        """
        return None

    def collect_changes(self):
        """
        Collects changes made to the object by iterating over instance
        attribute 'fields'.

        This method constructs the content of the table by iterating through
        each field
        listed in the 'fields' attribute. For each field, it checks if the
        field exists within the 'object' attribute. If the field has a
        corresponding
        display method (e.g., `get_field_display()`), it uses that method to
        retrieve
        the display value; otherwise, it retrieves the raw value of the field.
        Field names are formatted to replace underscores with spaces and
        capitalized
        for presentation. The resulting key-value pairs are appended to the
        'update_table' attribute.

        Notes:
            This method assumes that the 'fields' attribute contains a list
            of strings representing the names of fields to be displayed, and
            that the
            'object' attribute contains an instance of a model with the
            corresponding fields.
        """
        for field in self.fields:
            if hasattr(self.object, field):
                field_item = getattr(self.object, field)

                # Check if the field has choices and get the display value if
                # available
                if hasattr(self.object, f"get_{field}_display"):
                    field_item = getattr(self.object, f"get_{field}_display")()

                field = field.replace("_", " ")
                self.update_table.append(
                    [f"{field.capitalize()}: ", field_item])

    # METHODS FOR ACTION: LIST_FILTER and LIST:
    def get_queryset(self):
        """
        Requests the queryset of a model.

        Returns:
            queryset: Returns the requested queryset.
        """
        pass

    def get_user_queryset(self):
        """
        Requests the queryset of a model for a specific 'self.user'.

        Returns:
            queryset: Returns the requested queryset.
        """
        return None

    def user_choice(self, choice):
        """
        Asks the user to make a choice.

        Args:
             choice (dict): Contains the user's input from 'get_data' function.
        """
        pass

    def request_field_selection(self):
        """
        Prompts the user to choose the model attributes to make a filter.

        Returns:
            list: The list contains the choices of the user.
        """
        return None, None

    def choose_attributes(self):
        """
        Generates a table with a list of model attributes/fields that can be
        used for filtering.

        This method prepares a list of fields that the user can choose from
        when filtering data.
        It formats each field by replacing underscores with spaces and
        capitalizing the first
        letter. The formatted fields are then added to a table using the
        `create_pretty_table`
        function.

        The table is displayed to the user with the prompt "Which fields you
        want to filter?".

        The `fields` attribute of the instance is set to the list of fields
        that are to be
        displayed in the table.
        """
        pass

    def filter_selected_fields(self, selected_fields, order, user_queryset):
        """
        Filters and orders a queryset based on user-selected fields and order
        preference.

        This method takes a list of selected fields, an order preference, and
        a queryset of users.
        It maps the selected fields to their corresponding database fields
        using a predefined
        mapping. The queryset is then ordered by the selected fields in the
        specified order
        (ascending or descending).

        Args:
            selected_fields (list): A list of selected fields represented by
            single-letter codes.
            order (str): The order in which to sort the queryset, either 'A'
            for ascending or 'D'
                for descending.
            user_queryset (QuerySet): The queryset of users to be filtered and
            ordered.

        Returns:
            tuple: A tuple containing the filtered and ordered queryset
            ('filtered_queryset')and
                the list of fields used for ordering ('order').

        Raises:
            KeyError: If any of the selected fields are not found in the field
            mapping.
        """
        return None, None

    def display_result(self, filter_queryset, order_by_fields):
        """
        Displays a formatted table of client data based on the filtered
        queryset.

        This method constructs a dictionary of client data with each client's
        details keyed by their ID. It then uses the `create_queryset_table`
        function
        to display the data in a table format, with the option to order the
        data
        based on the fields specified in `order_by_fields`.

        Args:
            filter_queryset (QuerySet): A queryset of filtered client data.
            order_by_fields (list): A list of fields by which the data should
            be ordered.

        Returns:
            None: The function does not return a value; it displays the table
            directly.
        """
        pass

    # METHODS FOR ACTIONS: CREATE AND UPDATE:
    def create_table(self):
        """
        Creates a table with help of library: 'tabulate'. It takes the
        instance attribute
        'update_table' to create the table, 'cli/utils_tables.py'.
        """
        create_pretty_table(self.update_table)

    # METHODS FOR ACTION: UPDATE AND DELETE:
    def get_requested_model(self):
        """
        Prompt the user for the email or other required details to find the
        corresponding model.
        Displays a or several table(s) with help of 'cli/utils_table.py'.
        """
        pass

    # METHODS FOR ACTION: UPDATE:
    def get_fields_to_update(self):
        """
        Uses the 'multiple_choice_str_input' to retrieve the user's input.
        These choices will be
        transmitted to the 'get_data' method to call the necessary inputs.
        And sets the instance
        attribute 'field_to_update'.

        Returns:
            list: Contains a list of the option(s) which the user entered.
        """
        return self.fields_to_update

    def get_available_fields(self):
        """
        Sets the instance attribute 'available_fields'.

        Returns:
            dict: Contains the 'method', 'params' and 'label' to display in
            'get_data' the
            necessary input-types.
        """
        pass

    # METHODS FOR HANDLE:
    def list(self):
        """Methods when action='LIST' in the child Command."""
        self.get_queryset()
        self.get_instance_data()
        self.go_back()
        sys.exit()

    def list_filter(self):
        """Methods when action='LIST_FILTER' in the child Command."""
        self.get_queryset()
        if not self.queryset:
            create_info_message("No data available!")
            self.go_back()
            sys.exit()
        self.get_instance_data()
        choice = self.get_data()
        self.user_choice(choice)
        if choice["filter"] == "Y":
            self.choose_attributes()
            selected_fields, order = self.request_field_selection()
            user_queryset = self.get_user_queryset()
            filter_queryset, order_by_fields = self.filter_selected_fields(
                selected_fields, order, user_queryset
            )
            self.display_result(filter_queryset, order_by_fields)
            self.go_back()
            sys.exit()

    def create(self):
        """Methods when action='CREATE' in the child Command."""
        self.get_queryset()
        self.get_instance_data()
        validated_data = self.get_data()
        self.make_changes(validated_data)
        self.collect_changes()
        self.create_table()
        self.go_back()
        sys.exit()

    def update(self):
        """Methods when action='UPDATE' in the child Command."""
        self.get_queryset()
        if not self.queryset:
            create_info_message("No data available!")
            self.go_back()
            sys.exit()
        self.get_instance_data()
        self.get_requested_model()
        self.get_fields_to_update()
        self.get_available_fields()
        validated_data = self.get_data()
        self.make_changes(validated_data)
        self.collect_changes()
        self.create_table()
        self.go_back()
        sys.exit()

    def delete(self):
        """Methods when action='DELETE' in the child Command."""
        self.get_queryset()
        self.get_instance_data()
        self.get_requested_model()
        validated_data = self.get_data()
        self.make_changes(validated_data)
        self.collect_changes()
        self.go_back()
        sys.exit()

    def handle(self, *args, **options):
        """
        Handles the execution of the custom command based on the action
        specified.

        This method first calls the parent class's handle method to perform any
        necessary setup. Then it checks if the current user has the required
        permissions for the specified action. If the user lacks the necessary
        permissions, a permission denied message is displayed and the 'start'
        command is called. If the user has the correct permissions, the method
        dispatches to the appropriate method based on the action: LIST, CREATE,
        UPDATE, or DELETE.
        """
        super().handle(*args, **options)

        if self.user.employee_users.role not in self.permissions:
            create_permission_denied_message()
            call_command("start")
            sys.exit()

        if self.action == "LIST":
            self.list()
        elif self.action == "LIST_FILTER":
            self.list_filter()
        elif self.action == "CREATE":
            self.create()
        elif self.action == "UPDATE":
            self.update()
        elif self.action == "DELETE":
            self.delete()

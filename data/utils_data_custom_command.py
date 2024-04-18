from django.core.management import BaseCommand


class DataCreateCommand(BaseCommand):
    """
    This class is an abstract base class for creating data in the database
    using Django management commands. It provides a structure for defining the
    logic to gather data, create instances of models with that data, and handle
    the creation process.
    """

    help = "Custom BaseCommand to create fake data for employees, clients, contracts and events."

    def __init__(self, *args, **options):
        """
        Initialize the subclass attributes.
        """
        super().__init__(*args, **options)
        self.employee = None
        self.client = None
        self.contract = None
        self.event = None

    def get_queryset(self):
        """
        Creates the queryset and assigns it to `self.queryset`
        """
        pass

    def create_fake_data(self):
        """
        Creates the fake data with help of Faker(). For every model with
        different model attributes.

            Returns:
                 dict: Returns a dictionary with data of the created fake data.
        """
        return dict()

    def create_instances(self, data):
        """
        Retrieve the fake data of `create_fake_data` and creates the instances.
        If the model instance exists already it prints an 'exists already'
        message otherwise it confirms the creation of the model instances.

        Args:
            data (dict): Fake data to create the model instances.
        """
        pass

    def handle(self, *args, **options):
        """
        Handles the execution of the custom command.

        This method first calls the parent class's handle method to perform any
        necessary setup. A `queryset` is created for further operations.
        It creates the fake data and creates the model instances with the fake
        data.
        """

        self.get_queryset()
        fake_data = self.create_fake_data()
        self.create_instances(fake_data)

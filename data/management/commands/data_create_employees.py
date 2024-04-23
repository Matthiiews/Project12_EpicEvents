from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.contrib.auth.hashers import make_password

from data.utils_data_custom_command import DataCreateCommand
from faker import Faker
from accounts.models import Employee

from cli.utils_messages import create_error_message, create_success_message


UserModel = get_user_model()
fake = Faker()


class Command(DataCreateCommand):
    """
    Command to create 24 employees with basic data. This command generates and
    creates 24 employees with fake data. It assigns roles cyclically from a
    predefined list of roles ("SA", "SU", "MA").
    The command also generates random first names, last names, and emails for
    each employee.
    The password for each user is set to a default value. If there are any
    integrity errors during the creation process, it handles them
    appropriately.
    """

    help = "This command creates 24 employees as basic data."

    def get_queryset(self):
        pass

    def create_fake_data(self):
        roles_choices = ["SA", "SU", "MA"]
        data_employee = {}

        for i in range(1, 25):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@mail.com"

            # Use modulo operation to cycle through the roles
            role = roles_choices[(i - 1) % len(roles_choices)]
            employee = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
            }
            data_employee[i] = employee

        return data_employee

    @transaction.atomic
    def create_instances(self, data):
        try:
            users_to_create = []
            employees_to_create = []

            for value in data.values():
                user = UserModel(
                    email=value["email"],
                    password=make_password("TestPassw0rd!"))
                users_to_create.append(user)

                employee = Employee(user=user, first_name=value["first_name"],
                                    last_name=value["last_name"],
                                    role=value["role"])
                employees_to_create.append(employee)

            # Bulk create users and employees
            UserModel.objects.bulk_create(users_to_create)
            Employee.objects.bulk_create(employees_to_create)

        except IntegrityError:
            create_error_message("There are employees wich")
        else:
            self.stdout.write(data[1]["email"])
            create_success_message("Users and Employees", "created")

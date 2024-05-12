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
    Commande pour créer 24 employés avec des données de base. Cette commande
    génère et crée 24 employés avec des données fictives. Elle attribue les
    rôles cycliquement à partir d'une liste prédéfinie de rôles
    ("SA", "SU", "MA"). La commande génère également des prénoms, des noms de
    famille et des adresses e-mail aléatoires pour chaque employé. Le mot de
    passe de chaque utilisateur est défini sur une valeur par défaut.
    En cas d'erreurs d'intégrité pendant le processus de création, elles sont
    gérées de manière appropriée.

    Attributs :
        help (str) : Description de la commande.

    Méthods :
        get_queryset(self) : Méthode de substitution réservée pour une
        utilisation future.
        create_fake_data(self) : Génère des données fictives pour 24 employés
        et renvoie un dictionnaire avec ces données.
        create_instances(self, data) : Crée des instances des modèles User et
        Employee dans la base de données en utilisant les données fournies.

    Raises :
        IntegrityError : S'il y a une tentative de créer un employé qui viole
        les contraintes d'intégrité de la base de données.
    """

    help = "Cette commande crée 24 employés en tant que données de base."

    def get_queryset(self):
        pass

    def create_fake_data(self):
        roles_choices = ["SA", "SU", "MA"]
        data_employee = {}

        for i in range(1, 25):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@mail.com"

            # Utilisez l'opération de modulo pour parcourir les rôles en cycle.
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

            # Créez en masse des utilisateurs et des employés.
            UserModel.objects.bulk_create(users_to_create)
            Employee.objects.bulk_create(employees_to_create)

        except IntegrityError:
            create_error_message("There are employees wich")
        else:
            self.stdout.write(data[1]["email"])
            create_success_message("Users and Employees", "created")

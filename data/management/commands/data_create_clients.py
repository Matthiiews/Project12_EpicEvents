from django.db import IntegrityError
from faker import Faker

from data.utils_data_custom_command import DataCreateCommand
from cli.utils_messages import create_success_message, create_error_message

from accounts.models import Employee, Client

fake = Faker()


class Command(DataCreateCommand):
    """
    Commande pour créer des données de base pour 40 clients. Cette commande
    fait partie d'un système plus vaste de génération et de peuplement de la
    base de données avec des données de base sur les clients. Elle est conçue
    pour créer 40 clients avec divers attributs tels que le nom, l'e-mail,
    le téléphone et le nom de l'entreprise. Les clients sont associés à des
    employés ayant le rôle de "SA" (Ventes). Si un client avec le même e-mail
    existe déjà, une IntegrityError est capturée et gérée de manière
    appropriée.

    Attributes :
        - help (str) : Description de la commande.

    Méthods :
        - get_queryset(self) : Initialise le queryset pour les employés avec
        le rôle de "SA".
        - create_fake_data(self) : Génère des données fictives pour 40 clients
        et renvoie un dictionnaire avec les données.
        - create_instances(self, data) : Crée des instances du modèle Client
        dans la base de données en utilisant les données fournies.

    Raises :
        - IntegrityError : S'il y a une tentative de création d'un client avec
        un e-mail qui existe déjà dans la base de données.
    """

    help = "Cette commande crée 40 clients comme données de base."

    def get_queryset(self):
        self.employee = Employee.objects.filter(role="SA")

    def create_fake_data(self):
        data_client = {}

        for i in range(1, 41):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@mail.com"

            employee = self.employee[(i - 1) % len(self.employee)]

            client = {
                "employee": employee,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": fake.bothify("#######"),
                "company_name": fake.company(),
            }
            data_client[i] = client

        return data_client

    def create_instances(self, data):
        try:
            for d in data.values():
                Client.objects.create(**d)

        except IntegrityError:
            create_error_message("There are clients which")
        else:
            create_success_message("Clients", "created")

from django.db import IntegrityError
from faker import Faker

from accounts.models import Client
from cli.utils_messages import create_error_message, create_success_message
from data.utils_data_custom_command import DataCreateCommand
from contracts.models import Contract


fake = Faker()


class Command(DataCreateCommand):
    """
    Commande pour créer 30 contrats. Cette commande est conçue pour générer et
    créer 30 contrats avec des données fictives. Elle sélectionne des clients
    et des employés de manière aléatoire dans la base de données et les
    attribue à des contrats avec différents états. La commande génère
    également des coûts totaux et des montants payés fictifs pour chaque
    contrat. En cas d'erreurs d'intégrité pendant le processus de création,
    elle les gère de manière appropriée.

    Attributes :
        - `help` (str) : Description de la commande.

    Méthods :
        - `get_queryset(self)` : Initialise le queryset pour les clients,
        en les sélectionnant dans un ordre aléatoire.
        - `create_fake_data(self)` : Génère des données fictives pour 30
        contrats et renvoie un dictionnaire avec les données.
        - `create_instances(self, data)` : Crée des instances du modèle
        Contract dans la base de données en utilisant les données fournies.

    Raises :
        - `IntegrityError` : S'il y a une tentative de création d'un contrat
        qui viole les contraintes d'intégrité de la base de données.
    """

    help = "Cette commande crée 30 contrats."

    def get_queryset(self):
        self.client = Client.objects.select_related(
            "employee").all().order_by("?")

    def create_fake_data(self):
        state_choices = ["S", "S", "S", "D"]
        data_contract = {}

        for i in range(1, 31):
            client = self.client[(i - 1) % len(self.client)]
            state = state_choices[(i - 1) % len(state_choices)]

            contract = {
                "client": client,
                "employee": client.employee,
                "total_costs": fake.pydecimal(
                    left_digits=5, right_digits=2, positive=True),
                "amount_paid": fake.pydecimal(
                    left_digits=3, right_digits=2, positive=True),
                "state": state,
            }
            data_contract[i] = contract

        return data_contract

    def create_instances(self, data):
        try:
            for value in data.values():
                Contract.objects.create(**value)

        except IntegrityError:
            create_error_message("There are contracts wich")
        else:
            create_success_message("Contracts", "created")

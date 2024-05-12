from django.utils.timezone import make_aware
from django.db import IntegrityError

from data.utils_data_custom_command import DataCreateCommand
from cli.utils_messages import create_error_message, create_success_message

from events.models import Event
from contracts.models import Contract
from accounts.models import Employee

from faker import Faker

fake = Faker()


class Command(DataCreateCommand):
    """
    Commande pour créer 50 événements. Cette commande génère et crée 50
    événements avec des données fictives. Elle sélectionne aléatoirement des
    contrats et leurs employés associés dans la base de données et les
    attribue aux événements. La commande génère également des dates fictives,
    des noms d'événements, des emplacements et des notes pour chaque événement.
    Si des erreurs d'intégrité surviennent pendant le processus de création,
    elles sont gérées de manière appropriée.

    Attributs :
        - `help` (str) : Description de la commande.

    Méthods :
        - `get_queryset(self)` : Initialise la queryset pour les contrats, en
        les sélectionnant avec leurs employés associés.
        - `create_fake_data(self)` : Génère des données fictives pour 50
        événements et renvoie un dictionnaire avec les données.
        - `create_instances(self, data)` : Crée des instances du modèle Event
        dans la base de données en utilisant les données fournies.

    Raises :
        - `IntegrityError` : S'il y a une tentative de création d'un événement
        qui viole les contraintes d'intégrité de la base de données.
    """

    help = "Cette commande crée 50 événements."

    def get_queryset(self):
        self.contract = Contract.objects.filter(state="S")
        self.employee = Employee.objects.filter(role="SU")

    def create_fake_data(self):
        data_event = {}

        for i in range(1, 51):
            date_object = fake.date_time()
            date_object = make_aware(date_object)

            event_term = fake.word(ext_word_list=[
                "conference", "workshop", "meetup", "gathering"])

            contract = self.contract[(i - 1) % len(self.contract)]
            employee = self.employee[(i - 1) % len(self.employee)]

            event = {
                "contract": contract,
                "employee": employee,
                "date": date_object,
                "name": f"{fake.name()} {event_term}",
                "location": fake.address(),
                "max_guests": fake.random_int(min=50, max=1000),
                "notes": fake.text(),
            }
            data_event[i] = event

        return data_event

    def create_instances(self, data):
        try:
            for d in data.values():
                Event.objects.create(**d)

        except IntegrityError:
            create_error_message("There are events which")
        else:
            create_success_message("Events", "created")

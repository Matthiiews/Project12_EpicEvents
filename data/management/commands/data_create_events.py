from django.utils.timezone import make_aware
from django.db import IntegrityError

from data.utils_data_custom_command import DataCreateCommand
from cli.utils_messages import create_error_message, create_success_message

from events.models import Event
from contracts.models import Contract
from accounts.models import Employee

from faker import Faker

fake = Faker()


class command(DataCreateCommand):
    """
    Command to create 50 events. This command generates and creates 50 events
    with fake data. It selects contracts and their associated employees
    randomly from the database and assigns them to events. The command also
    generates fake dates, event names, locations, and notes for each event.
    If there are any integrity errors during the creation process, it handles
    them appropriately.
    """

    help = "This command creates 50 events."

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

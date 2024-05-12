from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator


class Event(models.Model):
    """
    Modèle représentant un événement.
    Ce modèle représente un événement avec divers attributs tels que contrat,
    employé, date, nom, lieu, max_guests et notes.

    - `contrat` (ForeignKey): Une clé étrangère vers le modèle Contract,
    représentant le contrat associé à l'événement.
    - `employé` (ForeignKey): Une clé étrangère vers le modèle Employee,
    représentant l'employé assigné à l'événement.
    - `date` (DateTimeField): La date et l'heure auxquelles l'événement est
    programmé.
    - `nom` (CharField): Le nom de l'événement.
    - `lieu` (CharField): L'adresse où l'événement aura lieu.
    - `max_guests` (PositiveIntegerField): Le nombre maximum d'invités
    autorisés pour l'événement.
    - `notes` (TextField): Notes ou détails supplémentaires sur l'événement.

    La méthode `__str__` retourne une représentation sous forme de chaîne de
    caractères de l'événement, comprenant son nom et l'e-mail de l'employé
    associé.
    """

    contract = models.ForeignKey("contracts.Contract", on_delete=models.CASCADE,
                                 related_name="event_contract",
                                 verbose_name=_("contract for event"))
    employee = models.ForeignKey("accounts.Employee", on_delete=models.CASCADE,
                                 related_name="event_employees",
                                 verbose_name=_("employee for event"))
    date = models.DateTimeField(default=timezone.now,
                                verbose_name=_("date of event"))
    name = models.CharField(max_length=100, verbose_name=_("name of event"))
    location = models.CharField(max_length=200,
                                verbose_name=_("address of event"))
    max_guests = models.PositiveIntegerField(
        default=1, validators=[
            MinValueValidator(
                1,
                _(
                    "Impossible to create an event with the number of guests less than 1 guest."))],
        verbose_name=_("number of guests"))
    notes = models.TextField(verbose_name=_("notes for the event"))

    def __str__(self):
        """
        String representation of Event object.
        """
        return f"{self.name} ({self.employee.user.email})"

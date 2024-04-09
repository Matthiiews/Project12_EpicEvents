from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator


class Event(models.Model):
    """
    Model representing an event.
    This model represents an event with various attributes such as contract,
    employee, date, name, location, max_guests, and notes.
    """

    contract = models.ForeignKey("accounts.Contract", on_delete=models.CASCADE,
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

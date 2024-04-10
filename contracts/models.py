from django.db import models
from django.utils.translation import gettext_lazy as _

from decimal import Decimal


class Contract(models.Model):
    """
    Model representing a contract.
    The `Contract` model represents a contract between a client and an
    employee within a system.
    It is designed to track the financial details of a contract, including the
    total costs, the amount paid, and the state of the contract (either signed
    or draft).
    """
    SIGNED = "S"
    DRAFT = "D"

    STATE_CHOICES = {SIGNED: _("Signed"), DRAFT: _("Draft")}

    client = models.ForeignKey("accounts.Client", on_delete=models.CASCADE,
                               related_name="contract_clients",
                               verbose_name=_("client of contract"))
    employee = models.ForeignKey("accounts.Employee", on_delete=models.CASCADE,
                                 related_name="contract_employees",
                                 verbose_name=_("employee of contract"))
    total_costs = models.DecimalField(max_digits=9, decimal_places=2,
                                      verbose_name=_(
                                          "total costs of contract"))
    amount_paid = models.DecimalField(max_digits=9, decimal_places=2,
                                      verbose_name=_(
                                          "paid amount of contract"))
    create_date = models.DateTimeField(auto_now_add=True,
                                       verbose_name=_("contract create on"))
    state = models.CharField(max_length=1, choices=STATE_CHOICES,
                             default=DRAFT, verbose_name=_("state"))

    @property
    def total(self):
        """
        Get the total costs of the contract.
        """
        return f"{self.total_costs} €"

    @property
    def paid_amount(self):
        """
        Get the amount paid for the contract.
        """
        return f"{self.amount_paid} €"

    @property
    def rest_amount(self):
        """
        Calculate and get the remaining amount to be paid for the contract.
        """
        # Convert the fields to Decimal before performing the calculation
        total_costs_decimal = Decimal(str(self.total_costs))
        amount_paid_decimal = Decimal(str(self.amount_paid))

        rest_amount = total_costs_decimal - amount_paid_decimal

        return f"{rest_amount} €"

    def __str__(self):
        """
        String representation of Contract object.
        """
        return f"{self.client.get_full_name} ({self.employee.user.email})"

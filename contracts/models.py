from django.db import models
from django.utils.translation import gettext_lazy as _

from decimal import Decimal


class Contract(models.Model):
    """
    Modèle représentant un contrat.
    Le modèle `Contrat` représente un contrat entre un client et un employé au
    sein d'un système. Il est conçu pour suivre les détails financiers d'un
    contrat, y compris les coûts totaux, le montant payé et l'état du contrat
    (signé ou brouillon).

    - `SIGNED` et `DRAFT` : Constantes représentant les états possibles dans
    lesquels un contrat peut se trouver.
    - `STATE_CHOICES` : Un dictionnaire associant les constantes d'état à des
    libellés lisibles par l'homme.

    - `client` (ForeignKey) : Une clé étrangère vers le modèle `Client`,
    indiquant le client associé au contrat.
    - `employee` (ForeignKey) : Une clé étrangère vers le modèle `Employé`,
    indiquant l'employé associé au contrat.
    - `total_costs` (DecimalField) : Un champ décimal représentant le coût
    total du contrat.
    - `amount_paid` (DecimalField) : Un champ décimal représentant le montant
    payé pour le contrat.
    - `create_date` (DateTimeField) : Un champ datetime automatiquement défini
    sur la date et l'heure actuelles lors de la création du contrat.
    - `state` (CharField) : Un champ de caractères avec des choix définis par
    `STATE_CHOICES`, indiquant l'état actuel du contrat.

    Les méthodes de propriété incluent :
    - `total` : Renvoie les coûts totaux du contrat formatés en tant que
    chaîne avec un symbole de devise.
    - `paid_amount` : Renvoie le montant payé pour le contrat formaté en tant
    que chaîne avec un symbole de devise.
    - `rest_amount` : Calcule le montant restant à payer sur le contrat en
    soustrayant le montant payé des coûts totaux, et le renvoie formaté en
    tant que chaîne avec un symbole de devise.

    La méthode `__str__` renvoie une représentation de chaîne du contrat,
    affichant le nom complet du client et l'e-mail de l'employé associé.

    Ce modèle est essentiel pour la gestion des contrats au sein d'une
    application Django, fournissant un moyen structuré de stocker et d'accéder
    aux informations contractuelles. L'utilisation de
    `on_delete=models.CASCADE` pour les clés étrangères `client` et `employee`
    garantit que lorsqu'un client ou un employé est supprimé, tous les
    contrats associés sont également supprimés pour maintenir l'intégrité des
    données.
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
        Obtiens les coûts totaux du contrat.
        """
        return f"{self.total_costs} €"

    @property
    def paid_amount(self):
        """
        Obtiens le montant payé pour le contrat.
        """
        return f"{self.amount_paid} €"

    @property
    def rest_amount(self):
        """
        Calcule et obtiens le montant restant à payer pour le contrat.
        """
        # Convertir les champs en décimal avant d'effectuer le calcul.
        total_costs_decimal = Decimal(str(self.total_costs))
        amount_paid_decimal = Decimal(str(self.amount_paid))

        rest_amount = total_costs_decimal - amount_paid_decimal

        return f"{rest_amount} €"

    def __str__(self):
        """
        Représentation sous forme de chaîne de caractères de l'objet Contrat.
        """
        return f"{self.client.get_full_name} ({self.employee.user.email})"

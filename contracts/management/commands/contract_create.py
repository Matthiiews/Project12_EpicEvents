import sys

from django.core.management import call_command


from cli.utils_custom_command import EpicEventsCommand
from cli.utils_tables import create_queryset_table
from cli.utils_messages import (
    create_does_not_exists_message, create_error_message,
    create_success_message)

from accounts.models import Client

from contracts.models import Contract


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour faciliter la création de nouveaux contrats au sein d'un système.
    Elle est spécifiquement adaptée aux utilisateurs ayant les permissions
    "MA", indiquant qu'elle est destinée à la gestion.

    - `help` : Une chaîne de caractères décrivant le but de la commande, qui
    est de demander les détails nécessaires pour créer un nouveau contrat.
    - `action` : Une chaîne de caractères indiquant l'action associée à cette
    commande, définie sur "CREATE".
    - `permissions` : Une liste de rôles autorisés à exécuter cette commande,
    dans ce cas, seul "MA" (Management) a la permission.

    Les méthodes clés de cette classe comprennent :

    - `get_queryset` : Initialise le queryset pour les objets `Contract`,
    sélectionnant les objets `Client` associés à chaque client.
    - `get_create_model_table` : Génère des tables de tous les contrats et un
    sous-ensemble de clients associés à l'employé avec le rôle ('SA') qui est
    responsable du client, affichant des informations pertinentes telles que
    l'email du client, les coûts totaux, le montant déjà payé, l'état du
    contrat et l'employé.
    - `get_data` : Demande à l'utilisateur de saisir les détails pour créer un
    nouveau contrat, capturant l'email du client, les coûts totaux, le montant
    payé et l'état du contrat.
    - `make_changes` : Valide si le client existe sinon il affiche un message
    d'erreur. Tente de créer un nouvel objet `Contract` avec les données
    fournies, en l'associant à l'objet `Employee` client responsable.
    Et vérifie si le contrat existe déjà.
    - `collect_changes` : Confirme la création d'un nouveau contrat et affiche
    un message de succès.
    - `go_back` : Offre la possibilité de revenir à la commande précédente,
    vraisemblablement à l'interface principale de gestion des contrats.

    Cette classe encapsule la fonctionnalité pour créer de nouveaux contrats,
    en veillant à ce que seuls les utilisateurs ayant les permissions
    appropriées puissent effectuer cette action. Elle tire parti de la classe
    `EpicEventsCommand` pour les fonctionnalités de commande communes, telles
    que l'affichage des invitations de saisie et la gestion de la saisie
    utilisateur.
    """

    help = "Demande les détails pour créer un nouveau contrat."
    action = "CREATE"
    permissions = ["MA"]

    def get_queryset(self):
        self.queryset = (
            Client.objects.select_related("employee")
            .only("employee__first_name", "employee__last_name",
                  "employee__role").filter(contract_clients__isnull=True).all()
        )

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for client in self.queryset:
            client_data = {
                "email": client.email,
                "name": client.get_full_name,
                "phone": client.phone,
                "company_name": client.company_name,
                "employee":
                    f"{client.employee.get_full_name} ({client.employee.role})"
            }
            table_data[f"Client {client.id}"] = client_data

        create_queryset_table(table_data, "Clients without a contract",
                              headers=self.headers["client"])

    def get_data(self):
        self.display_input_title("Enter details to create a new contract:")

        return {
            "client": self.email_input("Client email"),
            "total_costs": self.decimal_input("Amount of contract"),
            "amount_paid": self.decimal_input("Paid amount"),
            "state": self.choice_str_input(
                ("S", "D"), "State [S]igned or [D]raft"),
        }

    def make_changes(self, data):
        validated_data = dict()
        # Vérifie si le contrat existe déjà, client + contrat
        # OneToOne au lieu de ForeignKey? client

        client = Client.objects.filter(email=data["client"]).first()
        if not client:
            create_does_not_exists_message("Client")
            call_command("contract_create")
            sys.exit()

        validated_data["client"] = client
        validated_data["employee"] = client.employee

        # Supprime le client et l'employé pour les données :
        data.pop("client", None)

        # Vérifie si le contrat existe déjà :
        contract_exists = Contract.objects.filter(
            client=validated_data["client"]).exists()
        if contract_exists:
            create_error_message("Contract")
            call_command("contract_create")
            sys.exit()

        # create the contract:
        self.object = Contract.objects.create(
            client=validated_data["client"],
            employee=validated_data["employee"], **data)

    def collect_changes(self):
        self.fields = ["total", "paid_amount", "rest_amount", "state"]

        create_success_message("Contract", "created")
        self.update_table.append([f"Client: ", self.object.client.email])
        self.update_table.append(
            [f"Employee: ", self.object.employee.user.email])
        super().collect_changes()

    def go_back(self):
        call_command("contract")

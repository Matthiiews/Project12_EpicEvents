import sys

from django.core.management import call_command
from cli.utils_custom_command import EpicEventsCommand
from cli.utils_messages import create_permission_denied_message
from cli.utils_tables import create_queryset_table, create_pretty_table
from contracts.models import Contract


class Command(EpicEventsCommand):
    """
    Cette classe `Command` est une sous-classe de `EpicEventsCommand` conçue
    pour répertorier tous les contrats avec une option de filtrage basée sur
    l'entrée utilisateur. Elle est accessible aux utilisateurs ayant les
    permissions "SA", "SU" ou "MA".

    - `help` : Une chaîne décrivant l'objectif de la commande, qui est de
    répertorier tous les contrats et éventuellement de les filtrer.
    - `action` : Une chaîne indiquant l'action associée à cette commande,
    définie sur "LIST_FILTER" (LIST_FILTER).
    - `permissions` : Une liste de rôles autorisés à exécuter cette commande,
    dans ce cas, "SA" (Ventes), "SU" (Support) et "MA" (Management) ont la
    permission.

    Les principales méthodes de cette classe comprennent :

    - `get_queryset` : Initialise le queryset pour les objets `Contrat`,
    en sélectionnant les objets `Client` et `Employé` associés à chaque
    contrat.
    - `get_create_model_table` : Génère un tableau de tous les contrats,
    affichant des informations pertinentes telles que l'e-mail, le montant
    total, le montant payé, le montant restant, l'état et l'employé.
    - `get_data` : Invite l'utilisateur à décider s'il souhaite filtrer les
    contrats, capturant leur choix.
    - `user_choice` : Gère le choix de l'utilisateur de filtrer les contrats,
    avec une gestion spéciale pour les rôles "SA" et "MA" pour permettre le
    filtrage sans messages d'autorisation refusée.
    - `choose_attributes` : Affiche les champs disponibles pour le filtrage et
    permet à l'utilisateur de sélectionner les champs par lesquels il souhaite
    filtrer.
    - `request_field_selection` : Invite l'utilisateur à sélectionner des
    champs spécifiques pour le filtrage et à choisir l'ordre
    (ascendant ou descendant).
    - `get_user_queryset` : Filtre le queryset en fonction de la sélection de
    l'utilisateur et de sa préférence d'ordre.
    - `filter_selected_fields` : Applique les filtres et l'ordre sélectionnés
    au queryset, le préparant pour l'affichage.
    - `display_result` : Affiche la liste filtrée et ordonnée des contrats à
    l'utilisateur.
    - `go_back` : Fournit une option pour revenir à la commande précédente,
    probablement à l'interface principale de gestion des contrats.

    Cette classe encapsule la fonctionnalité de répertorier et éventuellement
    filtrer les contrats, en veillant à ce que seuls les utilisateurs ayant
    les permissions appropriées puissent effectuer ces actions. Elle utilise
    la classe `EpicEventsCommand` pour les fonctionnalités communes de
    commande, telles que l'affichage des invites de saisie et la gestion de
    l'entrée utilisateur.
    """

    help = "Liste de tous les contrats."
    action = "LIST_FILTER"
    permissions = ["SA", "SU", "MA"]

    def get_queryset(self):
        self.queryset = (
            Contract.objects.select_related("client", "employee").only(
                "client__email", "employee__first_name", "employee__last_name",
                "employee__role").all())

    def get_instance_data(self):
        super().get_instance_data()
        table_data = dict()

        for contract in self.queryset:
            contract_data = {
                "client": contract.client.email,
                "total": contract.total,
                "paid": contract.paid_amount,
                "rest": contract.rest_amount,
                "state": contract.get_state_display(),
                "employee":
                    f"{contract.employee.get_full_name} ({contract.employee.role})"
            }
            table_data[f"Contract {contract.id}"] = contract_data

        create_queryset_table(
            table_data, "Contracts", headers=self.headers["contract"])

    def get_data(self):
        self.display_input_title("Enter choice:")

        return {"filter": self.choice_str_input(
            ("Y", "N"), "Do you want ti filter your clients? [Y]es or [N]o")}

    def user_choice(self, choice):
        if choice["filter"] == "Y" and self.user.employee_users.role in ["SA", "MA"]:
            self.stdout.write()
            return
        elif choice["filter"] == "Y":
            create_permission_denied_message()
            call_command("contract")
            sys.exit()
        elif choice["filter"] == "N":
            self.stdout.write()
            call_command("contract")
            sys.exit()

    def choose_attributes(self):
        self.fields = ["client", "total_amount", "amount_paid", "state"]

        client_table = []
        for field in self.fields:
            field = field.replace("_", " ")
            formated_field = [f"[{field[0].upper()}]{field[1:]}"]
            client_table.append(formated_field)
        create_pretty_table(client_table, "Which fields you want to filter?")

    def request_field_selection(self):
        self.display_input_title("Enter choice:")

        selected_fields = self.multiple_choice_str_input(
            ("C", "T", "A", "S"), "Your choice? [C, T, A, S]")

        # ascendant ou descendant
        order = self.choice_str_input(
            ("A", "D"), "Your choice ? [A]scending or [D]escending")
        self.stdout.write()
        return selected_fields, order

    def get_user_queryset(self):
        # Si un employé MA est authentifié, créez un queryset avec tous les
        # employés SA.
        if self.user.employee_users.role == "MA":
            return self.queryset.filter(employee__role="SA")

        # Si un employé SA est authentifié, créez un queryset de cet employé
        # SA.
        return self.queryset.filter(employee__user=self.user)

    def filter_selected_fields(self, selected_fields, order, user_queryset):
        field_mapping = {
            "C": "client", "T": "total_costs", "A": "amount_paid", "S": "state"
            }

        order_by_fields = [
            f"{'_' if order == 'D' else ''}{field_mapping[field]}"
            for field in selected_fields]

        filter_queryset = user_queryset.order_by(*order_by_fields)

        return filter_queryset, order_by_fields

    def display_result(self, filter_queryset, order_by_fields):
        table_data = dict()

        headers = [
            "", "** Client email **", "Total amount", "Amount paid", "State"]

        for contract in filter_queryset:
            client_data = {
                "client": contract.client.email,
                "total_amount": contract.total_costs,
                "amount_paid": contract.amount_paid,
                "state": contract.state,
            }
            table_data[f"Contract {contract.id}"] = client_data

        create_queryset_table(
            table_data, "my Contracts", headers=headers,
            order_by_fields=order_by_fields)

    def go_back(self):
        call_command("contract")

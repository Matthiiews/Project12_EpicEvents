import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, call_command
from django.core.validators import validate_email
from django.utils.timezone import make_aware

from cli.utils_menu import BOLD, ENDC, style_text_display, BLUE
from cli.utils_messages import (
    create_invalid_error_message,
    create_permission_denied_message,
    create_info_message,
)
from cli.utils_tables import create_pretty_table
from cli.utils_token_mixin import JWTTokenMixin


class EpicEventsCommand(JWTTokenMixin, BaseCommand):
    """
    Commande de gestion personnalisée pour gérer des événements épiques.

    Attributs de classe :
        action (str): L'action à effectuer (LIST, CREATE, UPDATE, DELETE).
        permissions (str): Le rôle requis pour accéder à la commande.

    Attributs d'instance :
        object (Any): L'objet à manipuler par la commande.
        queryset (Any): Le queryset est utilisé uniquement lorsque "action =
        'LIST'" et demande le queryset d'un modèle.
        fields (list): Une liste de champs à mettre à jour.
        fields_to_update (list): Une liste de champs qui doivent être mis à
        jour.
        available_fields (dict): Un dictionnaire de champs disponibles.
        update_table (list): Une liste représentant la table de mise à jour.

    Méthodes :
        __init__(self, *args, **options): Initialise la commande avec des
        options.
        handle(self): La méthode principale pour exécuter l'action de la
        commande.

    Note :
        - Assurez-vous que l'attribut `action` est défini sur l'une des
        valeurs suivantes : 'LIST', 'CREATE', 'UPDATE', 'DELETE'.
        - L'attribut `permissions` devrait être défini sur le rôle requis pour
        exécuter la commande.
    """

    help = "BaseCommand personnalisée pour gérer des événements épiques"
    action = None
    permissions = None

    def __init__(self, *args, **options):
        """
        Initialiser les attributs de sous-classe.
        """
        super().__init__(*args, **options)
        self.available_fields = dict()
        self.client = None
        self.employee = None
        self.fields = list()
        self.fields_to_update = list()
        self.headers = list()
        self.object = None
        self.queryset = None
        self.update_table = list()

    @classmethod
    def custom_input(cls, label):
        value = input(label)

        if value in ["", " "]:
            print()
            call_command("start")
            sys.exit()

        return value

    @classmethod
    def text_input(cls, label, required=True):
        """
        Demande à l'utilisateur une saisie de texte et gère les champs requis.

        Cette méthode affiche une invite à l'utilisateur avec un label donné
        et marque éventuellement le champ comme requis. Si le champ est marqué
        comme requis, la méthode s'assure que l'utilisateur fournit une entrée
        non vide. Si l'utilisateur ne fournit pas d'entrée ou entre seulement
        des espaces, la méthode appelle la commande 'start' et imprime une
        ligne vide. Si le champ n'est pas requis ou si l'utilisateur fournit
        une entrée valide, la méthode renvoie la valeur d'entrée.

        Args:
            label (str): Le label à afficher à côté de l'invite de saisie.
            required (bool, facultatif): Indique si le champ de saisie est
            requis. Par défaut, True.

        Returns:
            str: La saisie de l'utilisateur en tant que chaîne de caractères.

        Raises:
            ValueError: Si la saisie est requise mais non fournie.
        """
        original_label = label

        if required:
            label = f"{label}*"
        label = f"{'':^5}{BOLD}{label}{ENDC}: "

        value = cls.custom_input(label)
        if not value and required:
            create_invalid_error_message("input")
            value = cls.text_input(original_label, required=required)

        return value

    @classmethod
    def int_input(cls, label, required=True):
        """
        Demande à l'utilisateur une saisie de nombre/entier et gère les champs
        requis. La fonction peut être quittée avec '' ou ' '.

        Args:
            label (str): Le label à afficher à côté de l'invite de saisie.
            required (bool, facultatif): Indique si le champ de saisie est
            requis. Par défaut, True.

        Returns:
            int: La saisie de l'utilisateur en tant qu'entier.

        Notes:
            utilise une ValueError si la saisie de l'utilisateur est '', la
            commande 'start' sera appelée pour quitter la fonction.
        """
        original_label = label

        if required:
            label = f"{label}*"
        label = f"{'':^5}{BOLD}{label}{ENDC}: "

        try:
            value = int(cls.custom_input(label))
        except ValueError:
            print("Invalid input! Number input.")
            value = cls.int_input(original_label, required=required)

        return value

    @classmethod
    def decimal_input(cls, label, required=True):
        """
        Demande à l'utilisateur une saisie de nombre décimal/à virgule
        flottante et gère les champs requis.

        Args:
            label (str): Le label à afficher à côté de l'invite de saisie.
            required (bool, facultatif): Indique si le champ de saisie est
            requis. Par défaut, True.

        Returns:
            float: La saisie de l'utilisateur en tant que nombre décimal/à
            virgule flottante.

        Raises:
            InvalidOperation: Si la saisie n'est pas un nombre décimal.
        """
        original_label = label

        if required:
            label = f"{label}*"
        label = f"{'':^5}{BOLD}{label}{ENDC}: "

        value = cls.custom_input(label)

        try:
            value = Decimal(value)
        except InvalidOperation:
            print("Invalid input! Decimal input.")
            value = cls.decimal_input(original_label, required=required)

        return value

    @classmethod
    def choice_str_input(cls, options, label, required=True):
        """
        Demande à l'utilisateur de faire un choix parmi des options sous forme
        de chaîne de caractères et gère les champs requis.

        Args:
            options (tuple): Les options sont les choix possibles que
            l'utilisateur peut faire.
            label (str): Le label à afficher à côté de l'invite de saisie.
            required (bool, facultatif): Indique si le champ de saisie est
            requis. Par défaut, True.

        Returns:
            str: La saisie de l'utilisateur sous forme de chaîne de caractères.

        Notes:
            Si l'utilisateur entre '' ou ' ', le programme appelle la commande
            'start' pour sortir.
        """
        value = cls.text_input(label, required)

        if value not in options:
            value = cls.choice_str_input(options, label, required)

        return value

    @classmethod
    def choice_int_input(cls, options, label, required=True):
        """
        Demande à l'utilisateur de faire un choix parmi des options sous forme
        d'entier et gère les champs requis.

        Args:
            options (tuple): Les options sont les choix possibles que
            l'utilisateur peut faire.
            label (str): Le label à afficher à côté de l'invite de saisie.
            required (bool, facultatif): Indique si le champ de saisie est
            requis. Par défaut, True.

        Returns:
            int: La saisie de l'utilisateur sous forme d'entier.

        Notes:
            Si l'utilisateur entre '' ou ' ', le programme appelle la commande
            'start' pour sortir.
        """
        value = cls.int_input(label, required)

        if value not in options:
            value = cls.choice_int_input(options, label, required)
        if value in ["", " "]:
            print()
            call_command("start")
            sys.exit()

        return value

    @classmethod
    def multiple_choice_str_input(cls, options, label, required=True):
        """
        Demande à l'utilisateur de faire un ou plusieurs choix sous forme de
        saisie(s) de chaîne de caractères et gère les champs requis.

        Args:
            options (tuple): Les options sont les choix possibles que
            l'utilisateur peut faire.
            label (str): Le label à afficher à côté de l'invite de saisie.
            required (bool, facultatif): Indique si le champ de saisie est
            requis. Par défaut, True.

        Returns:
            list: La saisie de l'utilisateur sous forme de liste.

        Notes:
            Si l'utilisateur entre '' ou ' ', le programme appelle la commande
            'start' pour sortir.
        """
        values = cls.text_input(label, required)

        return [w for w in values if w in options]

    @classmethod
    def date_input(cls, label, required=True):
        """
        Demande à l'utilisateur une saisie de date au format : JJ/MM/AAAA et
        gère les champs requis.

        Args:
            label (str): Le libellé à afficher à côté de l'invite de saisie.
            required (bool, facultatif): Indique si le champ de saisie est
            requis. Par défaut, True.

        Returns:
            date: La saisie de l'utilisateur sous forme d'objet date.

        Notes:
            Si l'utilisateur entre '' ou ' ', le programme appelle la commande
            'start' pour sortir.
        """
        value = cls.text_input(label, required)  # DD/MM/YYYY

        try:
            # Enregistre la date donnée au format : 2025-12-15 00:00:00
            value = datetime.strptime(value, "%d/%m/%Y")
            # Rend l'objet datetime conscient du fuseau horaire.
            value = make_aware(value)
        except ValueError:
            value = cls.date_input(label, required)

        return value

    @classmethod
    def email_input(cls, label, required=True):
        """
        Récupère une adresse e-mail valide auprès de l'utilisateur et gère les
        champs obligatoires. La fonction intégrée 'validate_email' vérifie si
        l'adresse e-mail saisie est valide.

        Args :
            - label (str) : Le libellé à afficher à côté de la demande de
            saisie.
            - required (bool, facultatif) : Indique si le champ de saisie est
            obligatoire. Par défaut, True.

        Returns :
            - email : La saisie de l'utilisateur en tant qu'e-mail.

        Raises :
            - ValidationError : Utilise la ValidationError pour rappeler la
            fonction à nouveau si l'adresse e-mail est incorrecte.

        Notes :
            - Si l'utilisateur entre '' ou ' ', le programme appelle la
            commande 'start' pour quitter.
        """
        value = cls.text_input(label, required)

        try:
            validate_email(value)
        except ValidationError:
            value = cls.email_input(label, required)

        return value

    @classmethod
    def password_input(cls, label, required=True):
        """
        Demande à l'utilisateur une saisie de mot de passe valide et gère les
        champs obligatoires. La fonction intégrée 'validate_password' vérifie
        si la saisie du mot de passe correspond aux
        'settings.AUTH_PASSWORD_VALIDATORS'.

        Args :
            - label (str) : Le libellé à afficher à côté de la demande de
            saisie.
            - required (bool, facultatif) : Indique si le champ de saisie est
            obligatoire. Par défaut, True.

        Returns :
            - password : La saisie de l'utilisateur en tant que mot de passe.

        Raises :
            - ValidationError : Utilise la ValidationError pour rappeler la
            fonction à nouveau si le mot de passe ne correspond pas aux
            critères 'settings.AUTH_PASSWORD_VALIDATORS' et affiche le message
            d'erreur expliquant pourquoi le mot de passe n'est pas valide.

        Notes :
            - Si l'utilisateur entre '' ou ' ', le programme appelle la
            commande 'start' pour quitter.
        """
        value = cls.text_input(label, required)
        # value = maskpass.askpass(prompt=label, mask="*") if required else
        # input(label)

        try:
            validate_password(value)
        except ValidationError as e:
            print(f"{'':^4}", e.messages)
            value = cls.password_input(label, required)

        return value

    @classmethod
    def display_input_title(cls, text):
        """
        Affiche un titre au-dessus de l'entrée.

        Args:
             text (str): Le texte est le titre imprimé au-dessus de l'entrée.
        """
        style_text_display(f"{'':^3}{text} {'':^3}", color=BLUE, bold=True)

    def display_new_line(self):
        """
        Imprime une nouvelle ligne.
        """
        print()

    # METHODS FOR ALL ACTIONS: (LIST, LIST_FILTER, CREATE, UPDATE AND DELETE):
    def get_instance_data(self):
        """
        Dans cette méthode, créez une table des instances de modèle existantes.
        """
        self.headers = {
            "employee": ["", "** Employee email **" "", "Name", "Role"],
            "client": [
                "",
                "** Client email **",
                "Name",
                "Phone",
                "Company name",
                "Employee",
            ],
            "contract": [
                "",
                "** Client email **",
                "Total amount",
                "Amount paid",
                "Rest amount",
                "State",
                "Employee",
            ],
            "event": [
                "",
                "** Client email **",
                "Date",
                "Name",
                "Location",
                "Max guests",
                "Employee",
            ],
        }
        pass

    # METHODS FOR ACTIONS: (LIST_FILTER, CREATE, UPDATE AND DELETE):
    def get_data(self):
        """
        Demande à l'utilisateur des données/informations.

        Returns:
            dict: Obtient l'entrée de l'utilisateur et la stocke dans un
            dictionnaire.
        """
        return dict()

    def go_back(self):
        """
        Appelle une autre commande.
        """
        pass

    # METHODS FOR ACTIONS: CREATE, UPDATE AND DELETE:
    def make_changes(self, data):
        """
        Vérifie si l'entrée de l'utilisateur de 'get_data' existe. Effectue
        des requêtes pour vérifier l'entrée de l'utilisateur dans la base de
        données. Effectue les modifications : 'create', 'update' ou 'delete'.

        Args:
            data (dict): Contient l'entrée de l'utilisateur à partir de la
            fonction 'get_data'.

        Errors :
            Lance différents messages d'erreur, qui sont définis dans
            'cli/utils_messages.py'.
        """
        return None

    def collect_changes(self):
        """
        Recueille les modifications apportées à l'objet en itérant sur
        l'attribut d'instance 'fields'.

        Cette méthode construit le contenu de la table en itérant à travers
        chaque champ répertorié dans l'attribut 'fields'. Pour chaque champ,
        elle vérifie si le champ existe dans l'attribut 'object'. Si le champ
        a une méthode d'affichage correspondante (par exemple,
        `get_field_display()`), elle utilise cette méthode pour récupérer la
        valeur d'affichage ; sinon, elle récupère la valeur brute du champ.
        Les noms de champ sont formatés pour remplacer les tirets bas par des
        espaces et sont capitalisés pour la présentation. Les paires
        clé-valeur résultantes sont ajoutées à l'attribut 'update_table'.

        Notes :
            Cette méthode suppose que l'attribut 'fields' contient une liste
            de chaînes représentant les noms des champs à afficher, et que
            l'attribut 'object' contient une instance d'un modèle avec les
            champs correspondants.
        """
        for field in self.fields:
            if hasattr(self.object, field):
                field_item = getattr(self.object, field)

                # Vérifiez si le champ a des choix et obtenez la valeur
                # d'affichage si disponible.
                if hasattr(self.object, f"get_{field}_display"):
                    field_item = getattr(self.object, f"get_{field}_display")()

                field = field.replace("_", " ")
                self.update_table.append(
                    [f"{field.capitalize()}: ", field_item])

    # METHODS FOR ACTION: LIST_FILTER and LIST:
    def get_queryset(self):
        """
        Demande le queryset d'un modèle.

        Returns :
            queryset : Renvoie le queryset demandé.
        """
        pass

    def get_user_queryset(self):
        """
        Demande le queryset d'un modèle pour un 'self.user' spécifique.

        Returns :
            queryset : Renvoie le queryset demandé.
        """
        return None

    def user_choice(self, choice):
        """
        Demande à l'utilisateur de faire un choix.

        Args :
            choice (dict) : Contient l'entrée de l'utilisateur de la fonction
            'get_data'.
        """
        pass

    def request_field_selection(self):
        """
        Demande à l'utilisateur de choisir les attributs du modèle pour
        effectuer un filtre.

        Returns :
            list : La liste contient les choix de l'utilisateur.
        """
        return None, None

    def choose_attributes(self):
        """
        Génère un tableau avec une liste d'attributs/champs de modèle pouvant
        être utilisés pour le filtrage.

        Cette méthode prépare une liste de champs parmi lesquels l'utilisateur
        peut choisir lors du filtrage des données. Elle formate chaque champ
        en remplaçant les underscores par des espaces et en mettant la
        première lettre en majuscule. Les champs formatés sont ensuite ajoutés
        à un tableau à l'aide de la fonction `create_pretty_table`.

        Le tableau est affiché à l'utilisateur avec la question "Quels champs
        souhaitez-vous filtrer ?".

        L'attribut `fields` de l'instance est défini sur la liste des champs
        qui doivent être affichés dans le tableau.
        """
        pass

    def filter_selected_fields(self, selected_fields, order, user_queryset):
        """
        Filtre et ordonne une queryset en fonction des champs sélectionnés par
        l'utilisateur et de ses préférences d'ordre.

        Cette méthode prend une liste de champs sélectionnés, une préférence
        d'ordre et une queryset d'utilisateurs. Elle mappe les champs
        sélectionnés à leurs champs de base de données correspondants en
        utilisant un mapping prédéfini. Ensuite, la queryset est ordonnée par
        les champs sélectionnés dans l'ordre spécifié
        (ascendant ou descendant).

        Args :
            - selected_fields (list) : Une liste de champs sélectionnés
            représentés par des codes d'une seule lettre.
            - order (str) : L'ordre dans lequel trier la queryset, soit 'A'
            pour ascendant, soit 'D' pour descendant.
            - user_queryset (QuerySet) : La queryset des utilisateurs à
            filtrer et à ordonner.

        Returns :
            - tuple : Un tuple contenant la queryset filtrée et ordonnée
            ('filtered_queryset') et la liste des champs utilisés pour
            l'ordonnancement ('order').

        Raises :
            - KeyError : Si l'un des champs sélectionnés n'est pas trouvé dans
            le mapping des champs.
        """
        return None, None

    def display_result(self, filter_queryset, order_by_fields):
        """
        Affiche un tableau formaté des données client basé sur la queryset
        filtrée.

        Cette méthode construit un dictionnaire des données client avec les
        détails de chaque client indexés par leur ID. Ensuite, elle utilise la
        fonction `create_queryset_table` pour afficher les données sous forme
        de tableau, avec l'option de trier les données en fonction des champs
        spécifiés dans `order_by_fields`.

        Args :
            - filter_queryset (QuerySet) : Une queryset des données client
            filtrées.
            - order_by_fields (list) : Une liste de champs par lesquels les
            données doivent être triées.

        Returns :
            - None : La fonction ne retourne pas de valeur ; elle affiche
            directement le tableau.
        """
        pass

    # METHODS FOR ACTIONS: CREATE AND UPDATE:
    def create_table(self):
        """
        Crée un tableau à l'aide de la bibliothèque 'tabulate'. Il utilise
        l'attribut d'instance 'update_table' pour créer le tableau,
        'cli/utils_tables.py'.
        """
        create_pretty_table(self.update_table)

    # METHODS FOR ACTION: UPDATE AND DELETE:
    def get_requested_model(self):
        """
        Demander à l'utilisateur l'e-mail ou d'autres détails requis pour
        trouver le modèle correspondant.
        Affiche un ou plusieurs tableaux à l'aide de 'cli/utils_table.py'.
        """
        pass

    # METHODS FOR ACTION: UPDATE:
    def get_fields_to_update(self):
        """
        Utilise 'multiple_choice_str_input' pour récupérer l'entrée de
        l'utilisateur.
        Ces choix seront transmis à la méthode 'get_data' pour appeler les
        saisies nécessaires.
        Et définit l'attribut d'instance 'field_to_update'.

        Retourne :
            list : Contient une liste de l'option(s) que l'utilisateur a
            saisie.
        """
        return self.fields_to_update

    def get_available_fields(self):
        """
        Définit l'attribut d'instance 'available_fields'.

        Returns :
            dict : Contient la 'méthode', les 'params' et le 'label' à
            afficher dans 'get_data' les types de saisie nécessaires.
        """
        pass

    # METHODS FOR HANDLE:
    def list(self):
        """
        Méthodes lorsque action='LIST' dans la commande enfant.
        """
        self.get_queryset()
        self.get_instance_data()
        self.go_back()
        sys.exit()

    def list_filter(self):
        """
        Méthodes lorsque action='LIST_FILTER' dans la commande enfant.
        """
        self.get_queryset()
        if not self.queryset:
            create_info_message("No data available!")
            self.go_back()
            sys.exit()
        self.get_instance_data()
        choice = self.get_data()
        self.user_choice(choice)
        if choice["filter"] == "Y":
            self.choose_attributes()
            selected_fields, order = self.request_field_selection()
            user_queryset = self.get_user_queryset()
            filter_queryset, order_by_fields = self.filter_selected_fields(
                selected_fields, order, user_queryset
            )
            self.display_result(filter_queryset, order_by_fields)
            self.go_back()
            sys.exit()

    def create(self):
        """
        Méthodes lorsque l'action est 'CREATE' dans la commande enfant.
        """
        self.get_queryset()
        self.get_instance_data()
        validated_data = self.get_data()
        self.make_changes(validated_data)
        self.collect_changes()
        self.create_table()
        self.go_back()
        sys.exit()

    def update(self):
        """
        Méthodes lorsque l'action est 'UPDATE' dans la commande enfant.
        """
        self.get_queryset()
        if not self.queryset:
            create_info_message("No data available!")
            self.go_back()
            sys.exit()
        self.get_instance_data()
        self.get_requested_model()
        self.get_fields_to_update()
        self.get_available_fields()
        validated_data = self.get_data()
        self.make_changes(validated_data)
        self.collect_changes()
        self.create_table()
        self.go_back()
        sys.exit()

    def delete(self):
        """
        Méthodes lorsque l'action est 'DELETE' dans la commande enfant.
        """
        self.get_queryset()
        self.get_instance_data()
        self.get_requested_model()
        validated_data = self.get_data()
        self.make_changes(validated_data)
        self.collect_changes()
        self.go_back()
        sys.exit()

    def handle(self, *args, **options):
        """
        Gère l'exécution de la commande personnalisée en fonction de l'action
        spécifiée.

        Cette méthode appelle d'abord la méthode de gestion de la classe
        parent pour effectuer toute configuration nécessaire. Ensuite, elle
        vérifie si l'utilisateur actuel dispose des autorisations requises
        pour l'action spécifiée. Si l'utilisateur ne dispose pas des
        autorisations nécessaires, un message de refus d'autorisation est
        affiché et la commande 'start' est appelée. Si l'utilisateur dispose
        des autorisations correctes, la méthode est dirigée vers la méthode
        appropriée en fonction de l'action : LISTE, CRÉATION, MISE À JOUR ou
        SUPPRESSION.
        """
        super().handle(*args, **options)

        if self.user.employee_users.role not in self.permissions:
            create_permission_denied_message()
            call_command("start")
            sys.exit()

        if self.action == "LIST":
            self.list()
        elif self.action == "LIST_FILTER":
            self.list_filter()
        elif self.action == "CREATE":
            self.create()
        elif self.action == "UPDATE":
            self.update()
        elif self.action == "DELETE":
            self.delete()

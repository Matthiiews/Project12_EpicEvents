from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle Utilisateur.
    La classe `UserManager` est un gestionnaire personnalisé pour le modèle
    `User`, étendant celui de Django, `BaseUserManager`. Elle fournit des
    méthodes pour créer des utilisateurs et des superutilisateurs, en veillant
    à ce que les adresses e-mail soient normalisées et que les
    superutilisateurs aient les autorisations appropriées.

    - `create_user`: Crée un nouvel utilisateur avec l'e-mail et le mot de
    passe donnés.
    Il normalise l'adresse e-mail et définit le mot de passe. Cette méthode est
    conçue pour gérer la création d'utilisateurs réguliers.
    - `create_superuser`: Crée un nouveau superutilisateur avec l'e-mail et le
    mot de passe donnés. Il veille à ce que les superutilisateurs aient
    `is_staff`, `is_superuser`, et `is_active` définis sur `True`.
    Cette méthode est spécifiquement pour créer des superutilisateurs avec
    toutes les autorisations.

    Ces méthodes sont essentielles pour gérer les comptes utilisateur dans une
    application Django, fournissant un moyen sécurisé et flexible de gérer
    l'authentification et l'autorisation des utilisateurs. En utilisant des
    méthodes personnalisées pour créer des utilisateurs et des
    superutilisateurs, le `UserManager` permet la mise en œuvre de logiques et
    de validations personnalisées qui correspondent aux exigences spécifiques
    de l'application.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Créer et enregistrer un utilisateur avec l'e-mail et le mot de passe
        donné.
        """
        if not email:
            raise ValueError(_("The Email must bet set"))
        if not password:
            raise ValueError(_("The Password must be set"))

        password = validate_password(password)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Créer et enregistrer un superutilisateur avec l'e-mail et le mot de
        passe donné.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Cette classe `User` est un modèle utilisateur personnalisé pour les
    applications Django, conçu pour utiliser les adresses e-mail comme
    identifiant principal pour l'authentification des utilisateurs au lieu des
    noms d'utilisateur traditionnels. Elle étend `AbstractUser` pour hériter
    de tous les champs et méthodes nécessaires à la gestion des utilisateurs,
    y compris l'authentification et l'autorisation.

    - `username` : Ce champ est défini sur `None` pour indiquer que les
    adresses e-mail seront utilisées pour l'authentification au lieu des noms
    d'utilisateur.
    - `email` (Champ d'e-mail) : Un `Champ d'e-mail` marqué comme unique,
    assurant que chaque adresse e-mail ne peut être associée qu'à un seul
    compte utilisateur.

    - `USERNAME_FIELD` : Spécifie le champ à utiliser comme identifiant unique
    pour l'authentification, qui est défini sur `'email'`.
    - `REQUIRED_FIELDS` : Spécifie les champs supplémentaires qui doivent être
    remplis lors de la création d'un utilisateur. Comme le champ e-mail est
    requis et unique, cette liste est vide.

    - `objects` : Affecte le gestionnaire personnalisé `UserManager` pour
    gérer la création d'instances d'utilisateur et de superutilisateur.

    La classe `UserManager`, `UserManager`, est un gestionnaire personnalisé
    pour le modèle `User`. Elle fournit des méthodes pour créer des
    utilisateurs et des superutilisateurs, en veillant à ce que les adresses
    e-mail soient normalisées et que les superutilisateurs aient les
    autorisations appropriées définies.

    - `create_user` : Crée un nouvel utilisateur avec l'e-mail et le mot de
    passe donnés. Il normalise l'adresse e-mail et définit le mot de passe.
    - `create_superuser` : Crée un nouveau superutilisateur avec l'e-mail et
    le mot de passe donnés. Il veille à ce que les superutilisateurs aient
    `is_staff`, `is_superuser`, et `is_active` définis sur `True`.

    Ce modèle utilisateur personnalisé permet un flux d'authentification plus
    simple, où les utilisateurs se connectent en utilisant leurs adresses
    e-mail, et il fournit une base flexible pour personnaliser les
    fonctionnalités de gestion des utilisateurs dans les applications Django.
    """

    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """
        Représentation textuelle de l'objet Utilisateur.
        """
        return self.email


class Employee(models.Model):
    """
    Le modèle `Employé` représente les employés dans le système, avec
    différents rôles tels que Ventes, Support et Gestion. Chaque employé est
    associé à un compte utilisateur, permettant l'authentification et
    l'autorisation en fonction de leur rôle.

    - `CHOIX_DE_ROLE` : Un dictionnaire définissant les rôles possibles qu'un
    employé peut avoir, y compris Ventes, Support et Gestion.

    - `utilisateur` (Clé étrangère) : Une relation un à un avec le modèle
    `Utilisateur`, établissant un lien entre un employé et son compte
    utilisateur. Ce champ est crucial pour l'authentification et
    l'autorisation.
    - `prenom` et `nom` (Charfield) : Champs Char pour stocker le prénom et
    le nom de famille de l'employé.
    - `role` (Charfield) : Un champ char avec des choix définis par
    `CHOIX_DE_ROLE`, spécifiant le rôle de l'employé dans l'organisation.

    Les méthodes de propriété incluent :
    - `obtenir_nom_complet` : Une méthode de propriété qui retourne le nom
    complet de l'employé, combinant le prénom et le nom de famille.
    - `obtenir_adresse_email` : Une méthode de propriété qui récupère
    l'adresse e-mail associée à l'utilisateur.

    La méthode `__str__` retourne une représentation textuelle de l'employé,
    affichant leur nom complet et leur rôle.
    """

    SALES = "SA"
    SUPPORT = "SU"
    MANAGEMENT = "MA"

    ROLE_CHOICES = {
        SALES: _("Sales"),
        SUPPORT: _("Support"),
        MANAGEMENT: _("Management"),
    }

    user = models.OneToOneField(
        "accounts.user", on_delete=models.CASCADE,
        related_name="employee_users", verbose_name=_("employee"),
    )
    first_name = models.CharField(max_length=100, verbose_name=_("first name"))
    last_name = models.CharField(max_length=100, verbose_name=_("last name"))
    role = models.CharField(max_length=2, choices=ROLE_CHOICES,
                            verbose_name=_("role"))

    @property
    def get_full_name(self):
        """
        Get the full name of the employee.
        """
        return f"{self.first_name} {self.last_name}"

    @property
    def get_email_address(self):
        """
        Get the email address of the associated user.
        """
        return self.user.email

    def __str__(self):
        """
        String representation of Employee object.
        """
        return f"{self.get_full_name} {self.role}"


class Client(models.Model):
    """
    Modèle Client représentant un client.
    Le modèle `Client` représente les clients associés aux employés dans le
    système. Chaque client est lié à un employé, indiquant qui est responsable
    de leur compte.

    - `employe` (Clé étrangère) : Une relation de clé étrangère vers le modèle
    `Employé`, reliant chaque client à son employé assigné.
    - `email` (Champ d'e-mail) : Un champ d'e-mail qui stocke l'adresse e-mail
    du client, assurant l'unicité pour éviter les doublons d'entrées clients.
    - `prenom`, `nom`, `telephone` et `nom_de_la_societe` (Charfield) :
    Champs Char pour stocker les informations personnelles du client et le nom
    de la société.
    - `creer_le` et `derniere_mise_a_jour` : Champs DateTime qui enregistrent
    automatiquement les temps de création et de dernière mise à jour d'un
    enregistrement client.

    Les méthodes de propriété incluent :
    - `obtenir_nom_complet` : Une méthode de propriété qui retourne le nom
    complet du client, combinant le prénom et le nom de famille.
    - `obtenir_adresse_email` : Une méthode de propriété qui récupère
    l'adresse e-mail de l'employé associé.

    La méthode `__str__` retourne une représentation textuelle du client,
    affichant leur nom complet.

    Ces modèles sont essentiels pour gérer les employés et les clients au sein
    d'une application Django, fournissant un moyen structuré de stocker et
    d'accéder aux informations utilisateur et client. Les relations entre les
    modèles garantissent que chaque client est associé à un employé,
    facilitant le contrôle d'accès basé sur les rôles et la gestion des
    données.
    """
    employee = models.ForeignKey("accounts.Employee", on_delete=models.CASCADE,
                                 related_name="client_employee",
                                 verbose_name=_("employee"))
    email = models.EmailField(
        max_length=254, unique=True, verbose_name=_("email address"))
    first_name = models.CharField(max_length=100, verbose_name=_("first name"))
    last_name = models.CharField(max_length=100, verbose_name=_("last name"))
    phone = models.CharField(max_length=17, verbose_name=_("phone number"))
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name=_("create on"))
    last_update = models.DateTimeField(
        auto_now=True, verbose_name=_("last updated on"))
    company_name = models.CharField(
        max_length=200, verbose_name=_("company name"))

    @property
    def get_full_name(self):
        """
        Obtenir le nom complet du client.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """
        Représentation textuelle de l'objet Client.
        """
        return f"{self.get_full_name} ({self.employee.get_full_name})"

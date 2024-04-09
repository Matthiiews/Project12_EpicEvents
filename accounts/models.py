from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    The `UserManager` class is a custom manager for the `User` model,
    extending Django's.
    `BaseUserManager`. It provides methods for creating users and superusers,
    ensuring that email addresses are normalized and that superusers have the
    appropriate permissions set.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
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
        Create and save a SuperUser with the given email and password.
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
    Custom User model extending AbstractUser.
    This class `User` is a custom user model for Django applications, designed
    to use email addresses as the primary identifier for user authentication
    instead of traditional usernames.
    It extends `AbstractUser` to inherit all the fields and methods necessary
    for user management, including authentication and authorization.
    """

    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        """
        String representation of User object.
        """
        return self.email


class Employee(models.Model):
    """
    Employee model representing an employee.
    The `Employee` model represents employees within the system, with
    different roles such as Sales, Support, and Management.
    Each employee is associated with a user account, allowing for
    authentication and authorization based on their role.
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
    Client model representing a client.
    The `Client` model represents clients associated with employees within
    the system.
    Each client is linked to an employee, indicating who is responsible for
    their account.
    """
    employee = models.ForeignKey("accounts.Employee", on_delete=models.CASCADE,
                                 related_name="client_employee",
                                 verbose_name=_("employee"))
    email = models.EmailField(
        max_length=254, unique=True, verbose_name=_("email address"))
    first_name = models.CharField(max_length=100, verbose_name=_("first name"))
    last_name = models.CharField(max_length=100, verbose_name=_("last name"))
    phone = models.CharField(max_length=17, verbose_name=_("Phone number"))
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name=_("create on"))
    last_update = models.DateTimeField(
        auto_now=True, verbose_name=_("last updated on"))
    company_name = models.CharField(
        max_length=200, verbose_name=_("company name"))

    @property
    def get_full_name(self):
        """
        Get the full name of the client.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        """
        String representation of Client object.
        """
        return f"{self.get_full_name} ({self.employee.get_full_name})"

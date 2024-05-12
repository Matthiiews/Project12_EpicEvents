from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

UserModel = get_user_model()


class Command(BaseCommand):
    """
    Cette commande est conçue pour créer un superutilisateur avec une adresse
    e-mail et un mot de passe spécifiés. Si un superutilisateur avec la même
    adresse e-mail existe déjà, elle affichera un message d'avertissement.
    Sinon, elle créera le superutilisateur et affichera un message de réussite.

    Attributs:
    help (str): Description de la commande.

    Méthodes:
        handle(self, *args, **options): Exécute la commande pour créer un
        superutilisateur.
            Args:
                *args: Liste d'arguments de longueur variable.
                **options: Arguments de mot-clé arbitraires.

            Returns:
                None

            Raises:
                IntegrityError: Si un superutilisateur avec la même adresse
                e-mail existe déjà.
    """

    help = "Cette commande crée un superutilisateur."

    def handle(self, *args, **options):
        try:
            UserModel.objects.create_superuser("admin@mail.com", "admin")
        except IntegrityError:
            self.stdout.write(self.style.WARNING("Exists already!"))
        else:
            self.stdout.write(
                self.style.SUCCESS("Superuser successfully created!"))

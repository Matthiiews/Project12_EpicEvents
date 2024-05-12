from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

UserModel = get_user_model


class Command(BaseCommand):
    """
    Cette commande est conçue pour créer un utilisateur avec une adresse
    e-mail et un mot de passe spécifiés. Si un utilisateur avec la même
    adresse e-mail existe déjà, elle affichera un message d'avertissement.
    Sinon, elle créera l'utilisateur et affichera un message de réussite.

    Attributes :
        help (str) : Description de la commande.

    Méthods :
        handle(self, *args, **options) : Exécute la commande pour créer un
        superutilisateur.
            Args :
                *args : Liste d'arguments de longueur variable.
                **options : Arguments de mots-clés arbitraires.

            Returns :
                None

            Raises :
                IntegrityError : Si un superutilisateur avec la même adresse
                e-mail existe déjà.
    """

    help = "Cette commande crée un utilisateur."

    def handle(self, *args, **options):
        try:
            UserModel.objects.create_user("e@mail.com", "TestPassw0rd!")
        except IntegrityError:
            self.stdout.write(self.style.WARNING("Exists already!"))
        else:
            self.stdout.write(self.style.SUCCESS("User successfully created!"))

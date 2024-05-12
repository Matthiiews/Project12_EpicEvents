from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

import jwt
import datetime

import os

from cli.utils_messages import (create_token_error_message,
                                create_does_not_exists_message,
                                create_invalid_error_message,
                                create_success_message
                                )


UserModel = get_user_model()

TOKEN_SECRET_KEY = "R2uKxYV6He92ocDkDDg6bdWvpceGrI2i"


class JWTTokenMixin:
    """
    Mixin pour gérer la génération de jetons JWT, la validation, la
    récupération de l'utilisateur et la gestion de la connexion.

    Cette mixin fournit des fonctionnalités pour générer un jeton JWT, valider
    le jeton, récupérer l'utilisateur correspondant et gérer la connexion si
    aucun jeton n'est disponible. Le jeton généré est enregistré dans un
    fichier nommé 'token.txt'.

    Attributs :
        help (str) : Une brève description de l'objectif et de la
            fonctionnalité de la mixin.
            Cette mixin est conçue pour être utilisée dans les commandes de
            gestion Django ou d'autres composants nécessitant la manipulation
            de jetons JWT.

        token (str) : Le jeton JWT généré ou récupéré par la mixin.
            Il est initialement défini sur None.

        payload (dict) : Le payload extrait du jeton JWT.
            Il est initialement défini sur None.

        user : L'objet utilisateur correspondant récupéré à partir du jeton
            JWT.
            Il est initialement défini sur None.

    Utilisation :
        1. Étendez votre commande de gestion Django ou d'autres composants
        avec cette mixin.
        2. Appelez les méthodes nécessaires pour générer, valider et manipuler
        le jeton JWT.

    Remarque :
        Assurez-vous que les dépendances requises pour la manipulation de JWT
        sont correctement installées (par exemple, la bibliothèque `pyjwt`).

        Le jeton généré est enregistré dans un fichier nommé 'token.txt'.
        Assurez-vous que les autorisations d'écriture appropriées sont
        accordées.
    """
    help = (
        "Mixin pour générer un jeton JWT, valider le jeton, récupérer l'utilisateur correspondant"
        "et gérer la connexion en l'absence de jeton. Le jeton sera enregistré dans un fichier : token.txt"
    )
    token = None
    payload = None
    user = None

    def generate_token(self, user_id, email,
                       expires_data=datetime.timedelta(hours=1)):
        """
        Générer un jeton JWT pour l'identifiant utilisateur et l'adresse
        e-mail donnés.

        Args:
            user_id (int): L'ID de l'utilisateur pour lequel le jeton est
            généré.
            email (str): L'adresse e-mail de l'utilisateur.
            expires_delta (datetime.timedelta, optionnel): La durée
            d'expiration du jeton.
                Par défaut, 1 heure.

        Returns:
            str: Le jeton JWT généré.

        Note:
            Cette fonction génère un jeton JWT avec l'identifiant utilisateur
            et l'e-mail fournis, en définissant les réclamations de date
            d'émission (iat) et d'expiration (exp) en conséquence.
            Le jeton est encodé en utilisant l'algorithme HMAC avec la
            SECRET_KEY fournie.
            Le jeton généré est ensuite enregistré dans le fichier spécifié
            dans le paramètre JWT_PATH.

        Raises:
            IOError: S'il y a une erreur lors de l'écriture du jeton dans le
            fichier.

        Example:
            token = generate_token(
                123, 'exemple@exemple.com', expires_delta=datetime.timedelta
                (days=7)
            )
        """
        # Valider les paramètres d'entrée.
        if not isinstance(user_id, int) or not isinstance(email, str) or not email:
            raise ValueError("Invalid user_id or email")

        now = datetime.datetime.utcnow()
        payload = {
            "user_id": user_id,
            "email": email,
            "iat": now,
            "exp": now + expires_data,
        }

        # Encoder la charge utile pour générer le jeton.
        token = jwt.encode(payload, TOKEN_SECRET_KEY, algorithm="HS256")

        # Enregistrer le jeton dans le fichier.
        try:
            with open(settings.JWT_PATH, "w") as file:
                file.write(token)
        except IOError as e:
            # Erreur lors de l'écriture dans le fichier.
            raise IOError(f"Error writing token to file: {e}")
        return token

    def verify_token(self):
        """
        Vérifiez le jeton JWT et enregistrez la charge utile dans l'attribut
        de classe payload.

        Returns:
            bool: True si le jeton est vérifié avec succès, False sinon.

        Raises/redirect:
            Si le jeton est expiré ou invalide, l'utilisateur sera redirigé
            pour se connecter à nouveau.
        """
        try:
            self.payload = jwt.decode(
                self.token, TOKEN_SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            self.login()
            self.get_user()
            return
        except jwt.InvalidTokenError:
            self.login()
            self.get_user()
            return

    def get_user(self):
        """
        Obtenez l'utilisateur correspondant au jeton.

        Returns:
            UserModel ou None: L'objet utilisateur correspondant s'il est
            trouvé, None sinon.
        """
        try:
            self.verify_token()
            if self.payload is None:
                return None
            user_id = self.payload.get("user_id")
            if user_id is not None:
                self.user = UserModel.objects.filter(id=user_id).first()
                return self.user
        except:
            create_token_error_message("There is a problem with the token")
            return None

    def login(self):
        """
        Cette méthode de connexion appelle get_login_data pour demander à
        l'utilisateur son email et son mot de passe.
        Et dans make_login_changes l'utilisateur sera authentifié et le jeton
        sera enregistré en tant qu'attribut de classe.
        """
        data = self.get_login_data()
        self.make_login_changes(data)

    def logout(self):
        """
        La méthode de déconnexion réinitialise l'attribut de classe payload et
        le jeton à None.
        Et écrase le fichier token.txt avec un contenu vide.
        """
        self.payload = None
        self.token = None
        with open(settings.JWT_PATH, "w") as file:
            file.write("")

    def get_login_data(self):
        """
        L'utilisateur sera invité à saisir l'adresse e-mail et le mot de passe
        pour se connecter.
        Retourne :
            l'email et le mot de passe en tant que données qui seront
            nécessaires dans make_login_changes.
        """
        self.stdout.write()
        self.display_input_title("Enter email and password to login:")
        return {
            "email": self.email_input("Email address"),
            "password": self.password_input("Password"),
        }

    def make_login_changes(self, data):
        """
        La fonction vérifie si un utilisateur avec l'adresse e-mail saisie
        existe. Si l'utilisateur existe, il sera authentifié. Lorsque
        l'utilisateur authentifié est trouvé, la méthode de classe
        generate_token sera appelée pour générer un jeton. Ce jeton sera
        enregistré dans l'attribut de classe token. Un message de réussite est
        affiché.
        Raises :
            Si l'adresse e-mail est incorrecte, une erreur est déclenchée.
        """
        email = data["email"]
        user_exists = UserModel.objects.filter(email=email).exists()

        if user_exists:
            user = authenticate(email=email, password=data["password"])

            if user is not None:
                self.token = self.generate_token(user.pk, user.email)

                create_success_message(
                    f"Employee [Role: {user.employee_users.role}]", "logged in"
                )
            else:
                create_invalid_error_message("email or password")
                self.login()
        else:
            create_does_not_exists_message("Email")

    def handle(self, *args, **options):
        """
        Gère l'exécution de la commande.

        Vérifie si le fichier token.txt existe, s'il n'existe pas, il crée le
        fichier sans aucun contenu. Lorsque le fichier token.txt existe, il
        lit le jeton et le sauvegarde dans l'attribut de classe token et
        appelle la méthode get_user pour associer un utilisateur au jeton.
        """
        file_path = settings.JWT_PATH  # "cli/token.txt"

        if not os.path.isfile(file_path):
            with open(file_path, "x") as file:
                pass

        with open(file_path, "r") as file:
            self.token = file.read()
            self.get_user()

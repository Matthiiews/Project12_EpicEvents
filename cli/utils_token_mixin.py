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
    Mixin to handle JWT token generation, validation, user retrieval, and
    login handling.

    This mixin provides functionality for generating a JWT token, validating
    the token, retrieving the corresponding user, and handling login if no
    token is available.
    The generated token is saved in a file named 'token.txt'.
    """
    help = (
        "Mixin to generate a JWT token, validate the token, get the corresponding user"
        "and handle the login if no token. The token will be saved in a file: token.txt"
    )
    token = None
    payload = None
    user = None

    def generate_token(self, user_id, email,
                       expires_data=datetime.timedelta(hours=1)):
        """
        Generate a JWT token for the given user ID and email.

        Args:
            user_id (int): The ID of the user for whom the token is generated.
            email (str): The email address of the user.
            expires_delta (datetime.timedelta, optional): The expiration time
            delta for the token.
                Defaults to 1 hour.

        Returns:
            str: The generated JWT token.
        """
        # Validate input parameters
        if not isinstance(user_id, int) or not isinstance(email, str) or not email:
            raise ValueError("Invalid user_id or email")

        now = datetime.datetime.utcnow()
        payload = {
            "user_id": user_id,
            "email": email,
            "iat": now,
            "exp": now + expires_data,
        }

        # Encode the payload to generate the token
        token = jwt.encode(payload, TOKEN_SECRET_KEY, algorithm="HS256")

        # Save the token to the file
        try:
            with open(settings.JWT_PATH, "w") as file:
                file.write(token)
        except IOError as e:
            # Error while writing ti the file
            raise IOError(f"Error writing token to file: {e}")
        return token

    def verify_token(self):
        """
        Verify the JWT token and save the payload inside the class attribute
        payload.

        Returns:
            bool: True if the token is successfully verified, False otherwise.

        Raises/redirect:
            If the token is expired or invalid the user will be redirected to
            log in again
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
        Get the corresponding user for the token.

        Returns:
            UserModel or None: The corresponding user object if found,
            None otherwise.
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
        This login method calls get_login_data to prompt the user for the
        email and the password.
        And in make_login_changes the user will be authenticated and the token
        will be saved as
        class attribute.
        """
        data = self.get_login_data()
        self.make_login_changes(data)

    def logout(self):
        """
        The logout method resets the class attribute payload and token to None.
        And overwrite
        the token.txt file with empty content.
        """
        self.payload = None
        self.token = None
        with open(settings.JWT_PATH, "w") as file:
            file.write("")

    def get_login_data(self):
        """
        The user will be prompt for the email address and the password to
        login.
        Returns:
            email and password as data which will be needed in
            make_login_changes.
        """
        self.stdout.write()
        self.display_input_title("Enter email and password to login:")
        return {
            "email": self.email_input("Email address"),
            "password": self.password_input("Password"),
        }

    def make_login_changes(self, data):
        """
        The function verifies if a User with prompted email exists. If the
        User exists, the user
        will be authenticated. When the authenticated user is found,
        the class method generate_token will be called to generate a token.
        This token will be saved in the class attribute token.
        A success message is displayed.
        Raises:
            If email address is wrong an error is thrown.
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
        Handle the command execution.

        Verifies if the file token.txt exists, if it does not exist, it
        creates the file without
        any content.
        When the file token.txt exists, it reads the token and saves it in the
        class attribute
        token and calls get_user method to associate a user to the token.
        """
        file_path = settings.JWT_PATH  # "cli/token.txt"

        if not os.path.isfile(file_path):
            with open(file_path, "x") as file:
                pass

        with open(file_path, "r") as file:
            self.token = file.read()
            self.get_user()

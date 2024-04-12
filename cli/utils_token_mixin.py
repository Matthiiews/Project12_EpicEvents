


UserModel = get_user_model()

TOKEN_SECRET_KEY = "R2uKxYV6He92ocDkDDg6bdWvpceGrI2i"


class JWTTokenMixin:
    """
    Mixin to handle JWT token generation, validation, user retrieval, and login handling.

    This mixin provides functionality for generating a JWT token, validating the token,
    retrieving the corresponding user, and handling login if no token is available.
    The generated token is saved in a file named 'token.txt'.
    """
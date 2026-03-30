from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom Authentication Backend:
    Allows a user to log in using either their exact username OR their email address.
    
    This replaces the default `ModelBackend` which only checks the username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # We start by ensuring we have a username/email to check against
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
            
        try:
            # Look up the user by matching the username exactly OR matching the email exactly (case-insensitive)
            # Q objects let us use the OR operator (|) in Django queries
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            
            # If a user is found, check if the password is correct
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except UserModel.DoesNotExist:
            # If no user was found, we run the default password hasher once.
            # This is a security measure to prevent "timing attacks", ensuring an attacker
            # can't guess if a username exists just by measuring how fast the server responds.
            UserModel().set_password(password)
            return None

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailPhoneUsernameBackend(ModelBackend):
    """
    This tells Django: "When someone tries to login, check if the text they typed
    matches a Username OR an Email OR a Phone Number."
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the input matches username, email, OR phone_number
            user = UserModel.objects.get(
                Q(username__iexact=username) | 
                Q(email__iexact=username) | 
                Q(phone_number__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None

        # If user found and password is correct
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
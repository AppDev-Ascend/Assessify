from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomLoginBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
    
    def authenticate(self, request, username=None, password=None):
        UserModel = get_user_model()
        
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

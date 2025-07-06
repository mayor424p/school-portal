from django.contrib.auth.backends import ModelBackend
from core.models import CustomUser

class AdmissionNumberBackend(ModelBackend):
    def authenticate(self, request, admission_number=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(admission_number=admission_number)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthenticationBackend(AuthenticationBackend):
    def authenticate(self, request, **credentials):
        email_or_phone = credentials.get("email")
        password = credentials.get("password")
        if email_or_phone and password:
            try:
                # Verifica se é email ou telefone
                if "@" in email_or_phone:
                    user = User.objects.get(email=email_or_phone)
                else:
                    user = User.objects.get(phone=email_or_phone)
                
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
        return None

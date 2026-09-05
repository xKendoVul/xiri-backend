from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Permite a los usuarios iniciar sesión tanto con su nombre de usuario (username)
    como con su dirección de correo electrónico (email).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if not username or not password:
            return None

        try:
            # Buscar por username exacto (insensible a mayúsculas) o por email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


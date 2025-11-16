import os
import jwt
from types import SimpleNamespace
from rest_framework import authentication, exceptions

JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("DJANGO_SECRET_KEY", "dev-secret"))
JWT_ALG = os.getenv("JWT_ALG", "HS256")

class JWTUserAuthentication(authentication.BaseAuthentication):
    """
    Lee Authorization: Bearer <token>, decodifica y crea un objeto usuario con:
    user.id, user.rol, user.institucion_id, user.email, user.nombre (si vienen)
    """
    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).decode("utf-8")
        if not auth or not auth.lower().startswith("bearer "):
            return None

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        except jwt.PyJWTError as e:
            raise exceptions.AuthenticationFailed(f"Token inválido: {e}")

        # Compatibilidad con distintos nombres de claims
        user_id = payload.get("id") or payload.get("user_id") or payload.get("sub")
        rol = payload.get("rol") or payload.get("role")
        institucion_id = payload.get("institucion_id") or payload.get("institution_id")
        email = payload.get("email")
        nombre = payload.get("nombre") or payload.get("name")

        if not user_id:
            raise exceptions.AuthenticationFailed("Token sin 'id' de usuario.")

        user = SimpleNamespace(
            is_authenticated=True,
            id=user_id,
            rol=rol,
            institucion_id=institucion_id,
            email=email,
            nombre=nombre,
        )
        return (user, payload)

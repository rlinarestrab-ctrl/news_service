from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

# Roles permitidos para acciones específicas
ROLES_PUBLICAR = {"admin", "institucion"}
ROLES_COMENTAR = {"admin", "institucion", "orientador", "estudiante"}


class PuedeVerPublicaciones(BasePermission):
    """
    Cualquiera puede ver las publicaciones (se filtran a nivel de queryset).
    """
    def has_permission(self, request, view):
        return True


class PuedePublicar(BasePermission):
    """
    Solo administradores o instituciones pueden crear nuevas publicaciones.
    """
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return (user.rol or "").lower() in ROLES_PUBLICAR


class PuedeComentar(BasePermission):
    """
    Permite comentar si el usuario está autenticado y su rol lo permite.
    """
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if request.method in SAFE_METHODS:
            return True
        if not user or not getattr(user, "is_authenticated", False):
            return False
        return (user.rol or "").lower() in ROLES_COMENTAR


class EsAutorOAdmin(BasePermission):
    """
    Permite editar/borrar publicaciones si es admin o el autor de la publicación.
    """
    def has_object_permission(self, request, view, obj):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if (user.rol or "").lower() == "admin":
            return True
        autor_id = str(getattr(obj, "autor_id", "")) if hasattr(obj, "autor_id") else None
        return autor_id and str(user.id) == autor_id


class EsDuenioComentarioOAdmin(BasePermission):
    """
    Permite editar/borrar comentarios si es admin o el autor del comentario.
    """
    def has_object_permission(self, request, view, obj):
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False
        if (user.rol or "").lower() == "admin":
            return True
        return str(obj.usuario_id) == str(user.id)

from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Categoria, Publicacion, Comentario, ComentarioRespuesta, Like
from .serializers import (
    CategoriaSerializer,
    PublicacionSerializer,
    ComentarioSerializer,
    ComentarioRespuestaSerializer,
    LikeSerializer,
)
from .permissions import (
    PuedePublicar,
    PuedeComentar,
    EsAutorOAdmin,
    EsDuenioComentarioOAdmin,
)

# -------------------- 🔹 CATEGORÍAS --------------------
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("nombre")
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------- 🔹 PUBLICACIONES --------------------
class PublicacionViewSet(viewsets.ModelViewSet):
    serializer_class = PublicacionSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "eliminar"]:
            if self.action in ["update", "partial_update", "destroy"]:
                return [EsAutorOAdmin()]
            return [PuedePublicar()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        q = Publicacion.objects.all().order_by("-fecha_publicacion")

        categoria = self.request.query_params.get("categoria")
        institucion_id = self.request.query_params.get("institucion_id")
        texto = self.request.query_params.get("q")
        estado = self.request.query_params.get("estado")

        if categoria:
            q = q.filter(categoria_id=categoria)
        if institucion_id:
            q = q.filter(autor_institucion_id=institucion_id)
        if texto:
            q = q.filter(Q(titulo__icontains=texto) | Q(contenido__icontains=texto))
        if estado:
            q = q.filter(estado=estado)

        rol = (
            (getattr(user, "rol", None) or "").lower()
            if user and getattr(user, "is_authenticated", False)
            else None
        )
        if rol == "admin":
            pass  # ve todo
        elif rol == "institucion":
            mine = Q(autor_id=str(user.id))
            published = Q(estado="publicado")
            q = q.filter(mine | published)
        else:
            q = q.filter(estado="publicado")

        return q

    def perform_create(self, serializer):
        user = self.request.user
        rol = (user.rol or "").lower()
        data = {
            "autor_id": user.id,
            "tipo_autor": "institucion" if rol == "institucion" else "usuario",
            "autor_institucion_id": getattr(user, "institucion_id", None)
            if rol == "institucion"
            else None,
        }
        serializer.save(**data)

    # -------------------- 🗑️ ELIMINAR PUBLICACIÓN --------------------
    @action(detail=True, methods=["delete"], permission_classes=[EsAutorOAdmin])
    def eliminar(self, request, pk=None):
        publicacion = self.get_object()
        user = request.user
        rol = (user.rol or "").lower()
        es_autor = str(publicacion.autor_id) == str(user.id)
        es_admin = rol == "admin"

        if not (es_admin or es_autor):
            return Response(
                {"detail": "Solo el administrador o el autor pueden eliminar esta publicación."},
                status=status.HTTP_403_FORBIDDEN,
            )

        publicacion.delete()
        return Response({"detail": "✅ Publicación eliminada correctamente."},
                        status=status.HTTP_204_NO_CONTENT)

    # -------------------- ❤️ LIKE / DISLIKE --------------------
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like_toggle(self, request, pk=None):
        pub = self.get_object()
        user = request.user
        like = Like.objects.filter(publicacion=pub, usuario_id=user.id).first()
        if like:
            like.delete()
            return Response({"liked": False})
        Like.objects.create(publicacion=pub, usuario_id=user.id)
        return Response({"liked": True})

    # -------------------- 💬 LISTAR COMENTARIOS --------------------
    @action(detail=True, methods=["get"], url_path="comentarios", permission_classes=[permissions.AllowAny])
    def listar_comentarios(self, request, pk=None):
        publicacion = self.get_object()
        comentarios = Comentario.objects.filter(publicacion=publicacion).order_by("-fecha_comentario")
        serializer = ComentarioSerializer(comentarios, many=True, context={"request": request})
        return Response(serializer.data)


# -------------------- 🔹 COMENTARIOS --------------------
class ComentarioViewSet(viewsets.ModelViewSet):
    """
    Gestiona comentarios de las publicaciones:
    - Crear comentario
    - Responder (subcomentarios tipo chat)
    - Eliminar (solo autor o admin)
    """
    queryset = Comentario.objects.all().select_related("publicacion")
    serializer_class = ComentarioSerializer
    permission_classes = [PuedeComentar]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action in ["destroy"]:
            return [IsAuthenticated(), EsDuenioComentarioOAdmin()]
        else:
            return [IsAuthenticated(), PuedeComentar()]

    # 🔹 Crear comentario principal
    def create(self, request, *args, **kwargs):
        user = request.user
        publicacion_id = request.data.get("publicacion")
        contenido = request.data.get("contenido")

        if not publicacion_id or not contenido:
            return Response({"detail": "Faltan campos obligatorios."},
                            status=status.HTTP_400_BAD_REQUEST)

        publicacion = get_object_or_404(Publicacion, id=publicacion_id)

        comentario = Comentario.objects.create(
            publicacion=publicacion,
            usuario_id=user.id,
            contenido=contenido
        )

        serializer = ComentarioSerializer(comentario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 🔹 Responder un comentario (tipo chat)
    @action(detail=True, methods=["post"], url_path="responder", permission_classes=[permissions.IsAuthenticated])
    def responder(self, request, pk=None):
        comentario_padre = get_object_or_404(Comentario, id=pk)
        contenido = request.data.get("contenido")
        user = request.user

        if not contenido:
            return Response({"detail": "El contenido no puede estar vacío."},
                            status=status.HTTP_400_BAD_REQUEST)

        respuesta = Comentario.objects.create(
            publicacion=comentario_padre.publicacion,
            usuario_id=user.id,
            contenido=contenido
        )

        ComentarioRespuesta.objects.create(
            comentario_padre=comentario_padre,
            comentario_respuesta=respuesta
        )

        return Response({"detail": "Respuesta creada correctamente."},
                        status=status.HTTP_201_CREATED)

    # 🔹 Eliminar comentario (admin o autor)
    def destroy(self, request, *args, **kwargs):
        comentario = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response({"detail": "No autenticado."}, status=status.HTTP_401_UNAUTHORIZED)

        if (str(comentario.usuario_id) != str(user.id)) and (user.rol or "").lower() != "admin":
            return Response({"detail": "No tienes permiso para eliminar este comentario."},
                            status=status.HTTP_403_FORBIDDEN)

        comentario.delete()
        return Response({"detail": "Comentario eliminado correctamente."},
                        status=status.HTTP_204_NO_CONTENT)

    # 🔹 Listar comentarios por publicación
    @action(detail=False, methods=["get"], url_path="de-publicacion/(?P<pub_id>[^/.]+)")
    def comentarios_de_publicacion(self, request, pub_id=None):
        comentarios = Comentario.objects.filter(publicacion_id=pub_id).order_by("fecha_comentario")
        serializer = ComentarioSerializer(comentarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Categoria, Publicacion, Comentario, ComentarioRespuesta, Like

User = get_user_model()

# ------------------ 🔹 CATEGORÍAS ------------------
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


# ------------------ 🔹 COMENTARIOS ------------------
class ComentarioSerializer(serializers.ModelSerializer):
    """
    Serializa los comentarios con:
    - nombre real del usuario (usuario_nombre)
    - fecha legible (fecha_formateada)
    - lista de respuestas tipo chat
    """
    usuario_nombre = serializers.SerializerMethodField()
    fecha_formateada = serializers.SerializerMethodField()
    respuestas = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = [
            "id",
            "publicacion",
            "usuario_id",
            "usuario_nombre",
            "contenido",
            "fecha_formateada",
            "respuestas",
        ]
        read_only_fields = (
            "usuario_id",
            "fecha_formateada",
            "usuario_nombre",
            "respuestas",
        )

    # 🔹 Nombre del usuario (desde el modelo o fallback)
    def get_usuario_nombre(self, obj):
        """
        Devuelve el nombre y apellido si existen,
        o correo, o fallback al UUID parcial.
        """
        try:
            user = User.objects.filter(id=obj.usuario_id).first()
            if user:
                nombre = getattr(user, "nombre", None)
                apellido = getattr(user, "apellido", None)
                if nombre or apellido:
                    return f"{nombre or ''} {apellido or ''}".strip()
                if getattr(user, "email", None):
                    return user.email
        except Exception:
            pass
        return f"Usuario {str(obj.usuario_id)[:8]}"

    # 🔹 Fecha legible (dd/mm/yyyy hh:mm)
    def get_fecha_formateada(self, obj):
        return obj.fecha_comentario.strftime("%d/%m/%Y %H:%M")

    # 🔹 Respuestas tipo chat (solo las del comentario actual)
    def get_respuestas(self, obj):
        """
        Devuelve solo las respuestas relacionadas con este comentario.
        """
        relaciones = (
            ComentarioRespuesta.objects.filter(comentario_padre=obj)
            .select_related("comentario_respuesta")
            .order_by("comentario_respuesta__fecha_comentario")
        )
        respuestas = [rel.comentario_respuesta for rel in relaciones]
        return ComentarioSerializer(respuestas, many=True, context=self.context).data


# ------------------ 🔹 RELACIÓN COMENTARIO/RESPUESTA ------------------
class ComentarioRespuestaSerializer(serializers.ModelSerializer):
    comentario_respuesta_contenido = serializers.CharField(
        source="comentario_respuesta.contenido", read_only=True
    )
    usuario_id = serializers.UUIDField(
        source="comentario_respuesta.usuario_id", read_only=True
    )

    class Meta:
        model = ComentarioRespuesta
        fields = [
            "id",
            "comentario_padre",
            "comentario_respuesta",
            "comentario_respuesta_contenido",
            "usuario_id",
        ]


# ------------------ 🔹 PUBLICACIONES ------------------
class PublicacionSerializer(serializers.ModelSerializer):
    comentarios_count = serializers.IntegerField(
        source="comentarios.count", read_only=True
    )
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)
    imagen = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Publicacion
        fields = "__all__"
        read_only_fields = (
            "autor_id",
            "autor_institucion_id",
            "tipo_autor",
            "vistas",
            "fecha_publicacion",
            "fecha_actualizacion",
        )

    # 🔹 Construir URL completa de la imagen
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")
        imagen_url = rep.get("imagen")
        if imagen_url and request:
            if imagen_url.startswith("/"):
                rep["imagen"] = request.build_absolute_uri(imagen_url)
        return rep


# ------------------ 🔹 LIKES ------------------
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = ("usuario_id",)

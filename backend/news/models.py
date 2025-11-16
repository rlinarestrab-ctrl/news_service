import uuid
from django.db import models

class Categoria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default="#000000")

    class Meta:
        indexes = [
            models.Index(fields=["nombre"]),
        ]

    def __str__(self):
        return self.nombre


class Publicacion(models.Model):
    ESTADOS = (
        ("borrador", "Borrador"),
        ("publicado", "Publicado"),
        ("archivado", "Archivado"),
    )
    TIPOS = (
        ("usuario", "Usuario"),
        ("institucion", "Institución"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    contenido = models.TextField()
    autor_id = models.UUIDField()  # referencia lógica a auth_service
    autor_institucion_id = models.UUIDField(blank=True, null=True)  # lógica a institution_service
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name="publicaciones")
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="borrador")
    imagen = models.ImageField(upload_to='publicaciones/', blank=True, null=True)
    vistas = models.IntegerField(default=0)
    tipo_autor = models.CharField(max_length=20, choices=TIPOS)

    class Meta:
        indexes = [
            models.Index(fields=["autor_id"], name="idx_publicaciones_autor"),
            models.Index(fields=["autor_institucion_id"], name="idx_publicaciones_institucion"),
            models.Index(fields=["categoria"], name="idx_publicaciones_categoria"),
            models.Index(fields=["estado"], name="idx_publicaciones_estado"),
        ]

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name="comentarios")
    usuario_id = models.UUIDField()  # lógica a auth_service
    contenido = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["publicacion"], name="idx_comentarios_publicacion"),
            models.Index(fields=["usuario_id"], name="idx_comentarios_usuario"),
        ]


class ComentarioRespuesta(models.Model):
    # Tabla de mapeo respuesta -> padre (1 a 1), fiel a tu SQL
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comentario_padre = models.ForeignKey(Comentario, on_delete=models.CASCADE, related_name="respuestas")
    comentario_respuesta = models.OneToOneField(Comentario, on_delete=models.CASCADE, related_name="respuesta_a")

    class Meta:
        indexes = [
            models.Index(fields=["comentario_padre"], name='idx_resp_padre'),
        ]


class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name="likes")
    usuario_id = models.UUIDField()
    fecha_like = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["publicacion", "usuario_id"], name="uniq_like_pub_usuario"),
        ]
        indexes = [
            models.Index(fields=["publicacion"], name="idx_likes_publicacion"),
            models.Index(fields=["usuario_id"], name="idx_likes_usuario"),
        ]


from django.contrib import admin
from .models import Categoria, Publicacion, Comentario, ComentarioRespuesta, Like

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "color")
    search_fields = ("nombre",)

@admin.register(Publicacion)
class PublicacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "estado", "tipo_autor", "autor_id", "autor_institucion_id", "vistas", "fecha_publicacion")
    list_filter = ("estado", "tipo_autor", "categoria")
    search_fields = ("titulo", "contenido")

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("publicacion", "usuario_id", "fecha_comentario")
    search_fields = ("contenido",)

@admin.register(ComentarioRespuesta)
class ComentarioRespuestaAdmin(admin.ModelAdmin):
    list_display = ("comentario_padre", "comentario_respuesta")

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("publicacion", "usuario_id", "fecha_like")

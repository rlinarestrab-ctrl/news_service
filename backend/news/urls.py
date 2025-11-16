from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, PublicacionViewSet, ComentarioViewSet
from django.conf import settings
from django.conf.urls.static import static

# 🔹 Registramos los routers de la API
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'publicaciones', PublicacionViewSet, basename='publicacion')
router.register(r'comentarios', ComentarioViewSet, basename='comentario')

# 🔹 Prefijo /api/ para mantener consistencia con los demás microservicios
urlpatterns = [
    path('api/', include(router.urls)),
]

# 🔹 Servir archivos locales (imágenes subidas desde tu computadora)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

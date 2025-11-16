import os
from pathlib import Path
import dj_database_url  # 👈 asegúrate de agregarlo a requirements.txt


BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad y entorno ---
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

# --- Aplicaciones instaladas ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "news",  # 👈 app principal
]

# --- Middleware ---
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "news_service.urls"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "news_service.wsgi.application"

# --- Base de datos ---
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Producción: usar DATABASE_URL (Supabase / Render)
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }

    # Permite definir el esquema vía variable de entorno
    DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
    DATABASES["default"]["OPTIONS"] = {
        "options": f"-c search_path={DB_SCHEMA},public"
    }

else:
    # Desarrollo local (Docker)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "news_service_db"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": int(os.getenv("POSTGRES_PORT", "5432")),
        }
    }

# --- Validadores de contraseñas (sin uso por ahora) ---
AUTH_PASSWORD_VALIDATORS = []

# --- Configuración regional ---
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Guatemala"
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos ---
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS (Cross-Origin Resource Sharing) ---
cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
if cors_origins_env:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_env.split(",")]
else:
    # Puedes agregar aquí tus orígenes de desarrollo o producción
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "https://orientacion-vocacional.onrender.com",
        "https://turutaeducativa.vercel.app",  # ejemplo producción
    ]

CORS_ALLOW_ALL_ORIGINS = not bool(CORS_ALLOWED_ORIGINS)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]

# --- JWT global (usado por authentication.py) ---
JWT_SECRET = os.getenv("JWT_SECRET", SECRET_KEY)
JWT_ALG = os.getenv("JWT_ALG", "HS256")

# --- Django REST Framework ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "news.authentication.JWTUserAuthentication",
    ],
}


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Si aún no tienes esto:
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
import os
from pathlib import Path
from datetime import timedelta
import json
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

SITE_ID = 1

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", False) == "True"

ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", "").split(",")
    if os.getenv("ALLOWED_HOSTS")
    else ["*"]
)

AUTH_USER_MODEL = 'core.User'

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Rechargement auto du navigateur : uniquement en local (DEBUG=True)
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]
    MIDDLEWARE += ["django_browser_reload.middleware.BrowserReloadMiddleware"]

ROOT_URLCONF = "david.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "david.wsgi.application"

# Base de données :
#  - en local (DEBUG=True)       -> SQLite (fichier db.sqlite3)
#  - en production (DEBUG=False) -> PostgreSQL via DATABASE_URL (Render)
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL est obligatoire quand DEBUG=False.")

    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,       # garde la connexion ouverte 10 min (plus rapide)
            conn_health_checks=True,
            ssl_require=True,       # Render exige SSL
        )
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "Africa/Abidjan"

USE_I18N = True

USE_TZ = True

# --- Fichiers statiques : fichiers du site (logo, CSS, JS, images du design) ---
# URL publique : /static/assets/blog-logo.png
STATIC_URL = "/static/"
# Où Django cherche TES fichiers statiques (en plus du dossier static/ de chaque app)
STATICFILES_DIRS = [BASE_DIR / "static"]
# Où collectstatic rassemble TOUT pour la production (ne pas modifier à la main)
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise sert les fichiers statiques en production (compressés + cache)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# --- Fichiers media : fichiers envoyés par les utilisateurs (uploads) ---
# URL publique : /media/<chemin du fichier>
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Erreur CSRF (formulaire expiré...) : on affiche notre page 403
CSRF_FAILURE_VIEW = "core.views.csrf_failure"

LOGIN_URL = "core:login"
LOGIN_REDIRECT_URL = "core:index"
LOGOUT_REDIRECT_URL = "core:index"

# En dev, les emails (reset password) sont affichés dans la console.
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@localhost")

# Production (HTTPS) : ex. CSRF_TRUSTED_ORIGINS=https://mon-app.onrender.com
CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

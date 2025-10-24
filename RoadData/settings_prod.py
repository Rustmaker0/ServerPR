from .settings import *  # берем все базовые настройки
import os
from pathlib import Path

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")]

if isinstance(BASE_DIR, str):
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    MEDIA_ROOT  = BASE_DIR / 'media'

STATIC_URL = '/static/'
MEDIA_URL  = '/media/'

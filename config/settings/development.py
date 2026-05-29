import os

from .base import * # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- Adicione o bloco abaixo para corrigir o erro de CSRF no Codespaces ---

# Identifica dinamicamente a URL do GitHub Codespaces
CODESPACE_NAME = os.getenv("CODESPACE_NAME")
if CODESPACE_NAME:
    CSRF_TRUSTED_ORIGINS = [
        f"https://{CODESPACE_NAME}-8000.app.github.dev",
        "https://localhost:8000",
        "http://localhost:8000",
    ]
else:
    CSRF_TRUSTED_ORIGINS = [
        "https://localhost:8000",
        "http://localhost:8000",
    ]
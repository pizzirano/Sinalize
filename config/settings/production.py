import os
from .base import * # noqa

# ─── SEGURANÇA E DEPLOY ──────────────────────────────────────────────────────
DEBUG = True

# Resgata o ALLOWED_HOSTS do seu .env. Se não achar, usa '*' como padrão seguro para o teste
ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", "*").split(",") if host.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

# Informa ao Django que ele está atrás de um proxy seguro da Cloudflare
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Libera o domínio da Cloudflare para evitar o erro 403 Forbidden de CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://sinalize.nodx.uk',
    'https://*.nodx.uk'
]
# ─── REDIRECIONAMENTOS DE AUTENTICAÇÃO ───────────────────────────────────────
# Define para onde o usuário vai após logar e deslogar com sucesso
LOGIN_REDIRECT_URL = '/catalog/home/'
LOGOUT_REDIRECT_URL = '/forms/login/'

# ─── CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS (WHITENOISE) ──────────────────────────
# Define onde o Django vai agrupar os arquivos no collectstatic
STATIC_ROOT = '/data/web/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/data/web/media'

# Injeta dinamicamente o WhiteNoise na lista de Middlewares vinda do base.py
# Ele precisa ficar logo após o SecurityMiddleware para funcionar corretamente
if 'django.middleware.security.SecurityMiddleware' in MIDDLEWARE:
    index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    MIDDLEWARE.insert(index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
else:
    MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Otimização do WhiteNoise para compactar (gzip/brotli) e criar hashes únicos dos arquivos
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ─── Base image ───────────────────────────────────────────────────────────────
FROM python:3.11.3-alpine3.18

LABEL maintainer="luis"

# ─── Variáveis de ambiente ────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# ─── Dependências do sistema ──────────────────────────────────────────────────
# nodejs + npm: necessário para compilar Tailwind CSS
# build-base + postgresql-dev: dependências Python (psycopg2)
# postgresql-client: pg_isready para health check
# bash: necessário para o entrypoint.sh
RUN apk add --no-cache \
    bash \
    build-base \
    postgresql-dev \
    postgresql-client \
    nodejs \
    npm

# ─── Virtualenv Python ────────────────────────────────────────────────────────
RUN python -m venv /venv

# ─── Dependências Python (camada cacheável) ───────────────────────────────────
# Copiado antes do restante do código para preservar cache do Docker.
# Se requirements.txt não mudar, essa camada não é reconstruída.
WORKDIR /Sinalize
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ─── Dependências Node (camada cacheável) ─────────────────────────────────────
# Mesma lógica: package.json e lock copiados antes do código.
# npm ci: instalação determinística (usa lock file, não atualiza versões)
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN cd frontend && npm ci

# ─── Código da aplicação ──────────────────────────────────────────────────────
COPY . .

# ─── Usuário não-root + permissões ───────────────────────────────────────────
# Criado antes de chmod para que chown funcione corretamente.
# /data/web/{static,media}: diretórios que o Django escreve (collectstatic, uploads)
RUN adduser -D duser && \
    mkdir -p /data/web/static /data/web/media && \
    chown -R duser:duser /Sinalize /data && \
    chmod +x /Sinalize/scripts/entrypoint.sh

USER duser

# ─── Entrypoint e comando padrão ─────────────────────────────────────────────
# ENTRYPOINT: prepara o ambiente (aguarda DB, build, migrate, collectstatic)
# CMD: processo principal — sobrescrito pelo docker-compose se necessário
ENTRYPOINT ["/bin/bash", "/Sinalize/scripts/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
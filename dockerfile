# ─── Base image ───────────────────────────────────────────────────────────────
FROM python:3.11.3-alpine3.18

LABEL maintainer="luis"

# ─── Variáveis de ambiente ────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

# Argumento para definir o arquivo de requisitos (Padrão: requirements.txt)
ARG REQUIREMENTS_FILE=requirements.txt

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
WORKDIR /Sinalize

# Copia tanto o arquivo da raiz quanto a pasta inteira de requirements
COPY requirements.txt ./
COPY requirements/ ./requirements/

# Condicional inteligente: se o arquivo existir dentro de 'requirements/', usa ele.
# Caso contrário, tenta ler da raiz do projeto.
RUN pip install --upgrade pip && \
    if [ -f "requirements/${REQUIREMENTS_FILE}" ]; then \
        pip install -r requirements/${REQUIREMENTS_FILE}; \
    else \
        pip install -r ${REQUIREMENTS_FILE}; \
    fi

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

FROM python:3.11.3-alpine3.18

LABEL mantainer="luis"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# dependências do sistema
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    postgresql-client \
    # netcat-openbsd removed: using pg_isready (postgres client) for readiness checks
    bash

# venv
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# diretório app
WORKDIR /Sinalize

# requirements primeiro (cache)
COPY requirements.txt /Sinalize/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# código
COPY . /Sinalize
COPY scripts /Sinalize/scripts

# permissões
RUN adduser -D duser && \
    mkdir -p /data/web/static /data/web/media && \
    chown -R duser:duser /Sinalize /data && \
    sed -i 's/\r$//' /Sinalize/scripts/commands.sh && \
    chmod +x /Sinalize/scripts/*.sh

USER duser

CMD ["/bin/sh", "-c", "tr -d '\\r' < /Sinalize/scripts/commands.sh > /tmp/commands.sh && /bin/sh /tmp/commands.sh"]
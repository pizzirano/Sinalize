FROM python:3.11.3-alpine3.18

LABEL maintainer="luis"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH"

RUN apk add --no-cache \
    bash \
    build-base \
    postgresql-dev \
    postgresql-client \
    nodejs \
    npm

RUN python -m venv /venv

WORKDIR /Sinalize

COPY requirements/development.txt requirements/base.txt ./requirements/
RUN pip install --upgrade pip && \
    pip install -r requirements/development.txt

COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm ci

COPY . .

RUN adduser -D duser && \
    mkdir -p /data/web/static /data/web/media && \
    chown -R duser:duser /Sinalize /data && \
    chmod +x /Sinalize/scripts/entrypoint.sh

USER duser

ENTRYPOINT ["/bin/bash", "/Sinalize/scripts/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
FROM python:3.11-slim

LABEL maintainer="luis"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 🔧 dependências + Node 20
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    bash \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# 👤 cria usuário
RUN useradd -m duser

# 🧠 venv
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# 📁 diretório app
WORKDIR /Sinalize

# 📦 dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 📁 código
COPY . .
COPY scripts ./scripts

# 📁 diretórios
RUN mkdir -p /data/web/static /data/web/media

# 🔥 permissões
RUN chown -R duser:duser /Sinalize /data

# 🔧 scripts
RUN sed -i 's/\r$//' /Sinalize/scripts/commands.sh && \
    chmod +x /Sinalize/scripts/*.sh

# 👤 usuário final
USER duser

CMD ["/bin/sh", "-c", "tr -d '\\r' < /Sinalize/scripts/commands.sh > /tmp/commands.sh && /bin/sh /tmp/commands.sh"]
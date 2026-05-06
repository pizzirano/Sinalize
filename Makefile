# ═══════════════════════════════════════════════════════════════
# Makefile — Sinalize Project Commands
# Uso: make <comando>
# ═══════════════════════════════════════════════════════════════

# ── Variáveis ──────────────────────────────────────────────────
CONTAINER=sinalize-projeto-1
DB_CONTAINER=sinalize-psql-1
MANAGE=docker exec -it $(CONTAINER) python manage.py

# ═══════════════════════════════════════════════════════════════
# 🐳 DOCKER — Ciclo de vida
# ═══════════════════════════════════════════════════════════════

up:
	# Sobe todos os containers em background
	docker compose up -d

up-build:
	# Rebuild completo da imagem + sobe (use após mudar Dockerfile ou requirements)
	docker compose up -d --build

down:
	# Para e remove os containers (preserva volumes)
	docker compose down

down-v:
	# Para containers E remove volumes (apaga banco de dados!)
	docker compose down -v

restart:
	# Reinicia apenas o container da aplicação Django
	docker compose restart projeto

logs:
	# Mostra logs em tempo real do container Django
	docker compose logs -f projeto

logs-db:
	# Mostra logs em tempo real do PostgreSQL
	docker compose logs -f psql

ps:
	# Lista containers rodando com status
	docker compose ps

# ═══════════════════════════════════════════════════════════════
# 🐚 SHELL — Acesso aos containers
# ═══════════════════════════════════════════════════════════════

sh:
	# Entra no shell do container Django (bash)
	docker exec -it $(CONTAINER) bash

sh-root:
	# Entra como root (para instalar pacotes ou debugar permissões)
	docker exec -it --user root $(CONTAINER) bash

sh-db:
	# Entra no shell do container PostgreSQL
	docker exec -it $(DB_CONTAINER) bash

# ═══════════════════════════════════════════════════════════════
# 🗄️ BANCO DE DADOS — Django + psql direto
# ═══════════════════════════════════════════════════════════════

migrate:
	# Aplica todas as migrações pendentes
	$(MANAGE) migrate --noinput

migrations:
	# Gera novas migrações baseadas nas mudanças dos models
	$(MANAGE) makemigrations

migrations-app:
	# Gera migrações para um app específico: make migrations-app app=catalog
	$(MANAGE) makemigrations $(app)

showmigrations:
	# Lista todas as migrações e seus status (✓ aplicada, [ ] pendente)
	$(MANAGE) showmigrations

sqlmigrate:
	# Mostra o SQL que uma migração vai executar: make sqlmigrate app=catalog num=0001
	$(MANAGE) sqlmigrate $(app) $(num)

dbshell:
	# Abre o cliente psql diretamente via Django (usa as credenciais do .env)
	$(MANAGE) dbshell

psql:
	# Abre o psql direto no container do banco (acesso raw ao PostgreSQL)
	docker exec -it $(DB_CONTAINER) psql -U $$POSTGRES_USER -d $$POSTGRES_DB

# ═══════════════════════════════════════════════════════════════
# 👤 SUPERUSER & USUÁRIOS
# ═══════════════════════════════════════════════════════════════

superuser:
	# Cria superuser de forma interativa (pede username, email, senha)
	$(MANAGE) createsuperuser

superuser-auto:
	# Cria superuser sem interação (útil em CI/CD)
	# Edite as variáveis abaixo ou passe via env
	docker exec -it $(CONTAINER) python manage.py shell -c "\
	from django.contrib.auth import get_user_model; \
	User = get_user_model(); \
	User.objects.create_superuser('admin', 'admin@sinalize.com', 'admin123') \
	if not User.objects.filter(username='admin').exists() \
	else print('Superuser já existe')"

changepassword:
	# Muda senha de um usuário: make changepassword user=admin
	$(MANAGE) changepassword $(user)

# ═══════════════════════════════════════════════════════════════
# 📦 STATIC FILES & FRONTEND
# ═══════════════════════════════════════════════════════════════

static:
	# Roda collectstatic (copia tudo para STATIC_ROOT)
	$(MANAGE) collectstatic --noinput --clear

tailwind-dev:
	# Compila Tailwind em modo dev (sem minify, mais rápido)
	docker exec -it $(CONTAINER) sh -c "cd /Sinalize/frontend && npm run build:dev"

tailwind-build:
	# Compila Tailwind para produção (minificado)
	docker exec -it $(CONTAINER) sh -c "cd /Sinalize/frontend && npm run build"

tailwind-watch:
	# Tailwind em modo watch (recompila ao salvar qualquer template)
	docker exec -it $(CONTAINER) sh -c "cd /Sinalize/frontend && npm run watch"

tailwind-version:
	# Verifica versão instalada do Tailwind no container
	docker exec -it $(CONTAINER) sh -c "cd /Sinalize/frontend && npm list tailwindcss"

# ═══════════════════════════════════════════════════════════════
# 🔍 DJANGO — Inspeção e utilitários
# ═══════════════════════════════════════════════════════════════

shell:
	# Abre o Django shell (Python com contexto Django carregado)
	$(MANAGE) shell

shell-plus:
	# Django shell com todos os models importados automaticamente
	# (requer django-extensions no requirements/development.txt)
	$(MANAGE) shell_plus

check:
	# Verifica configuração do Django sem rodar o servidor
	$(MANAGE) check

urls:
	# Lista todas as URLs registradas no projeto
	$(MANAGE) show_urls

diffsettings:
	# Mostra diferenças entre suas settings e os defaults do Django
	$(MANAGE) diffsettings

# ═══════════════════════════════════════════════════════════════
# 🧹 LIMPEZA
# ═══════════════════════════════════════════════════════════════

clean-pyc:
	# Remove arquivos .pyc e __pycache__ (resolve imports fantasma)
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-static:
	# Remove o staticfiles/ gerado (será regenerado pelo collectstatic)
	rm -rf staticfiles/

clean-node:
	# Remove node_modules (será reinstalado no próximo docker compose up --build)
	docker exec -it $(CONTAINER) rm -rf /Sinalize/frontend/node_modules

# ═══════════════════════════════════════════════════════════════
# 🚀 ATALHOS COMPOSTOS — Fluxos comuns
# ═══════════════════════════════════════════════════════════════

fresh:
	# Reset completo: derruba tudo, reconstrói, sobe
	# ⚠️ APAGA O BANCO — use só em dev
	docker compose down -v
	docker compose up -d --build

setup:
	# Sequência inicial após clonar o projeto
	docker compose up -d --build
	sleep 5
	$(MANAGE) migrate --noinput
	$(MANAGE) createsuperuser

mm:
	# makemigrations + migrate em sequência
	$(MANAGE) makemigrations
	$(MANAGE) migrate --noinput

.PHONY: up up-build down down-v restart logs logs-db ps \
        sh sh-root sh-db \
        migrate migrations showmigrations sqlmigrate dbshell psql \
        superuser superuser-auto changepassword \
        static tailwind-dev tailwind-build tailwind-watch tailwind-version \
        shell check urls diffsettings \
        clean-pyc clean-static clean-node \
        fresh setup mm
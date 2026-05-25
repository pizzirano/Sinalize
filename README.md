# Sinalize — Sinalário Digital de Libras

> Plataforma web para registro, busca e visualização de sinais em Libras, com foco no domínio **Turismo**. Projeto acadêmico do Instituto Federal Catarinense — Campus Camboriú.

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Django 5.x + Python 3.11 |
| Frontend | Tailwind CSS + Alpine.js + HTMX |
| Build CSS | Node.js + npm (`frontend/`) |
| Banco de dados | PostgreSQL |
| Containerização | Docker + Docker Compose |
| Componentes UI | Flowbite |
| Hot reload | django-browser-reload |
| Deploy | Não configurado |

---

## Estrutura do Projeto

```text
Sinalize/
├── apps/
│   ├── catalog/                  # Catálogo de sinais
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── views.py
│   │
│   └── forms/                    # Cadastro e formulários
│       ├── apps.py
│       ├── models.py
│       └── views.py
│
├── config/
│   ├── settings/
│   │   └── base.py               # Configuração principal Django
│   │
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── frontend/                     # Frontend e Tailwind
│   ├── package.json
│   ├── package-lock.json
│   ├── src/
│   │   └── input.css
│   └── dist/
│       └── output.css
│
├── templates/
│
├── static/
│
├── requirements/
│   ├── base.txt
│   └── development.txt
│
├── scripts/
│   └── entrypoint.sh
│
├── manage.py
├── Dockerfile
├── docker-compose.yml
└── .env
```

---

## Organização dos Apps Django

Todos os apps ficam dentro do diretório:

```text
apps/
```

O projeto utiliza **imports curtos**, por exemplo:

```python
from catalog.models import Video
```

**NÃO usar:**

```python
from apps.catalog.models import Video
```

Para isso funcionar, o Django adiciona automaticamente `apps/` ao `sys.path`.

Arquivo:

```text
config/settings/base.py
```

Trecho utilizado:

```python
import sys
from pathlib import Path

BASE_DIR = Path(
    __file__
).resolve().parent.parent.parent

sys.path.insert(
    0,
    str(BASE_DIR / "apps")
)
```

---

## Configuração dos Apps

Os apps utilizam nomes curtos no Django.

### INSTALLED_APPS

Arquivo:

```text
config/settings/base.py
```

Correto:

```python
INSTALLED_APPS = [
    ...
    "catalog",
    "forms",
]
```

Incorreto:

```python
"apps.catalog"
"apps.forms"
```

---

## AppConfig

### apps/catalog/apps.py

```python
from django.apps import AppConfig

class CatalogConfig(AppConfig):

    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = "catalog"
```

---

### apps/forms/apps.py

```python
from django.apps import AppConfig

class FormsConfig(AppConfig):

    default_auto_field = (
        "django.db.models.BigAutoField"
    )

    name = "forms"
```

---

## Pré-requisitos

Instalar:

- Docker Desktop
- Docker Compose
- Git

---

## Clonando o projeto

```bash
git clone https://github.com/seu-usuario/sinalize.git

cd sinalize
```

---

## Variáveis de ambiente

Criar:

```bash
cp .env.example .env
```

Exemplo:

```env
DEBUG=True

SECRET_KEY=sua-secret-key

DB_NAME=sinalize
DB_USER=postgres
DB_PASSWORD=postgres

DB_HOST=postgres
DB_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Subindo o projeto

Primeira execução:

```bash
docker compose up --build
```

Execuções seguintes:

```bash
docker compose up
```

O `entrypoint.sh` executa automaticamente:

1. Aguarda PostgreSQL
2. Compila frontend (Tailwind)
3. Executa migrations
4. Executa collectstatic
5. Inicializa Django

Aplicação:

```text
http://localhost:8000
```

Exemplo validado:

```text
http://localhost:8000/catalog/home/
```

---

## Docker atual

Imagem base:

```dockerfile
FROM python:3.11.3-alpine3.18
```

Pacotes instalados:

```dockerfile
RUN apk add --no-cache \
    bash \
    build-base \
    postgresql-dev \
    postgresql-client \
    nodejs \
    npm
```

Dependências frontend:

```dockerfile
COPY frontend/package.json \
     frontend/package-lock.json* \
     ./frontend/

RUN cd frontend && npm ci
```

Usuário não-root:

```dockerfile
RUN adduser -D duser
```

Execução:

```dockerfile
ENTRYPOINT [
    "/bin/bash",
    "/Sinalize/scripts/entrypoint.sh"
]
```

---

## Frontend

Local:

```text
frontend/
```

Build manual:

```bash
docker compose exec projeto \
sh -c "cd frontend && npm run build"
```

Modo desenvolvimento:

```bash
docker compose exec projeto \
sh -c "cd frontend && npm run dev"
```

Instalar dependência:

```bash
docker compose exec projeto \
sh -c "cd frontend && npm install pacote"
```

---

## Configuração Django

Arquivo:

```text
config/settings/base.py
```

Arquivos estáticos:

```python
STATIC_URL = "/static/"

STATIC_ROOT = (
    BASE_DIR / "staticfiles"
)

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

MEDIA_URL = "/media/"

MEDIA_ROOT = (
    BASE_DIR / "media"
)
```

Hot reload:

```python
if DEBUG:

    INSTALLED_APPS += [
        "django_browser_reload"
    ]

    MIDDLEWARE += [
        (
        "django_browser_reload.middleware."
        "BrowserReloadMiddleware"
        )
    ]
```

---

## Comandos úteis

Subir:

```bash
docker compose up
```

Reconstruir:

```bash
docker compose up --build
```

Parar:

```bash
docker compose down
```

Reiniciar Django:

```bash
docker compose restart projeto
```

Logs:

```bash
docker compose logs -f projeto
```

Entrar no container:

```bash
docker compose exec projeto bash
```

Criar migrations:

```bash
docker compose exec projeto \
python manage.py makemigrations
```

Aplicar migrations:

```bash
docker compose exec projeto \
python manage.py migrate
```

Criar admin:

```bash
docker compose exec projeto \
python manage.py createsuperuser
```

Instalar biblioteca Python:

```bash
docker compose exec -u 0 projeto \
pip install pacote
```

Atualizar:

```text
requirements/development.txt
```

---

## Fluxo de inicialização validado

Estado atual validado:

✅ `sys.path.insert()` configurado

✅ `catalog` importável

✅ `forms` importável

✅ `INSTALLED_APPS` corrigido

✅ migrations executando

✅ collectstatic funcionando

✅ Tailwind compilando

✅ servidor Django iniciado

✅ rota `/catalog/home/` retornando HTTP 200

---

## Produção (planejado)

Ainda não hospedado.

Checklist futuro:

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` por variável
- [ ] `ALLOWED_HOSTS`
- [ ] `CSRF_TRUSTED_ORIGINS`
- [ ] PostgreSQL externo
- [ ] Gunicorn
- [ ] Traefik / Nginx
- [ ] Volume persistente para `media/`

Estrutura recomendada:

```text
requirements/
├── base.txt
├── development.txt
└── production.txt
```

Produção:

```dockerfile
RUN pip install \
-r requirements/base.txt
```

---

## Acessibilidade

O projeto segue WCAG 2.1 AAA.

Objetivos:

### Comunidade surda

- Hierarquia visual clara
- Vídeos descritivos
- Conteúdo visual acessível

### Daltônicos

- Alto contraste
- Ícone + texto + cor

### Navegação

- `focus-visible`
- Navegação por teclado
- Skip links

Ferramentas:

- Lighthouse
- axe DevTools

Meta:

```text
Lighthouse >= 90
```

---

## Contribuição

Criar branch:

```bash
git checkout \
-b feature/SIN-XX-descricao
```

Executar:

```bash
docker compose up
```

Abrir Pull Request.

---

## Licença

Projeto acadêmico — Instituto Federal Catarinense — Campus Camboriú.
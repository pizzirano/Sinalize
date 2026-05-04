## versão 2025 ja atualizada na main aplicar ajustes para delploy na cloudflare Realizado merge com correções do contêiner feito: atualizar merge de brach atual e testada, SIN-3 Completa

## task Aual SIN-5- incluir requitements as novas libs da compiçação node do twailwind e criar o app Theme no respositorio Django django-htmx django-tailwind, ussar com p SIN-5: Instalação e Configuração do Django Tailwind
Este guia detalha o passo a passo para instalar e configurar o django-tailwind utilizando o ambiente Docker no seu projeto Sinalize, resolvendo problemas de permissão e estruturação de diretórios.

Passo 1: Instalação do Pacote
Instale o pacote django-tailwind com todos os recursos de desenvolvimento (incluindo cookiecutter e browser-reload). Utilize o usuário root no container para garantir permissões de escrita:

PowerShell
docker compose exec -u 0 projeto python -m pip install 'django-tailwind[cookiecutter,honcho,reload]'
Passo 2: Registrar o Tailwind no settings.py
Abra o arquivo projeto/settings.py e adicione o aplicativo tailwind na sua lista INSTALLED_APPS:

Python
INSTALLED_APPS = [
    'django.contrib.admin',
    'rest_framework',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',
    'forms',
    'tailwind',  # <- Adicione esta linha
]
Passo 3: Criação Correta do Aplicativo theme
Para evitar erros de módulo ou problemas de indentação em comandos do sistema, criaremos a estrutura diretamente pelo Django dentro do container:

Crie a pasta do app theme via terminal:

PowerShell
docker compose exec -u 0 projeto python manage.py startapp theme
Inicialize os arquivos do Tailwind:

PowerShell
docker compose exec -u 0 projeto python manage.py tailwind init
Quando solicitado o nome do app, digite: theme

Quando perguntado sobre o plugin DaisyUI, selecione a opção: 1 (no)

Passo 4: Ativação do Theme no settings.py
Adicione o novo aplicativo theme e configure o seu nome logo abaixo das suas INSTALLED_APPS no projeto/settings.py:

Python
INSTALLED_APPS = [
    'django.contrib.admin',
    'rest_framework',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',
    'forms',
    'tailwind',
    'theme',  # <- Adicione o theme aqui
]

TAILWIND_APP_NAME = "theme"
Passo 5: Instalação das Dependências do Tailwind
Instale os executáveis e as dependências do compilador:

PowerShell
docker compose exec -u 0 projeto python manage.py tailwind install
Passo 6: Configuração do django-browser-reload
Para que as atualizações de HTML e CSS recarreguem a página automaticamente no modo de desenvolvimento, configure o settings.py com o bloco condicional DEBUG:

Python
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]

    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]
E inclua as rotas do reload no seu projeto/urls.py principal:

Python
from django.urls import include, path
from django.conf import settings

urlpatterns = [
    # Suas outras rotas
]

if settings.DEBUG:
    urlpatterns += [
        path("reload/", include("django_browser_reload.urls")),
    ]
Passo 7: Utilização
Para iniciar o seu servidor de desenvolvimento junto com o compilador do Tailwind, utilize:

PowerShell
docker compose exec projeto python manage.py tailwind dev


docker compose restart projeto
##SIN-6- Selecionar os componentes de home no Flowbite e incluir em playground.html

tutorial no munual antes do docker compose exec -u 0 projeto mkdir -p theme
docker compose exec -u 0 projeto touch theme/__init__.py

docker compose exec -u 0 projeto sh -c "echo 'from django.apps import AppConfig' > theme/apps.py"
docker compose exec -u 0 projeto sh -c "echo 'class ThemeConfig(AppConfig):' >> theme/apps.py"
docker compose exec -u 0 projeto sh -c "echo \"    default_auto_field = 'django.db.models.BigAutoField'\" >> theme/apps.py"
docker compose exec -u 0 projeto sh -c "echo \"    name = 'theme'\" >> theme/apps.py"
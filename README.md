# Sinalize — Sinalário Digital em LIBRAS

> Repositório sistematizado de sinais em Língua Brasileira de Sinais (LIBRAS), desenvolvido como plataforma web acessível para a comunidade surda, estudantes, professores e tradutores.

## Sobre o Projeto

O **Sinalize** é uma aplicação web para organizar, buscar e disponibilizar sinais em LIBRAS, reduzindo barreiras comunicacionais por meio de um repositório visual e multimodal da língua.

O sistema funciona como um **sinalário digital**: associa termos da língua oral a registros visuais em vídeo, organizados em uma hierarquia de domínios, categorias e subcategorias. O projeto está vinculado ao **Edital PIBITI nº 110/2023 do IFC/CNPq** e foca inicialmente no domínio de **Turismo**, com 70 sinais cadastrados para atender à demanda da região litorânea de Santa Catarina.

## Recursos Principais

| Recurso | Descrição |
|---|---|
| **Categorização Hierárquica** | Organização em domínios → categorias → subcategorias |
| **Flexibilidade Relacional** | Um mesmo termo pode pertencer a múltiplos contextos |
| **Busca Viva (HTMX)** | Filtro as-you-type sem recarregamento de página |
| **Acessibilidade WCAG 2.1 AAA** | Alto contraste, navegação por teclado e skip links |
| **Gestão Multimodal de Vídeos** | Classificação por tipo: Sinal, Datilologia e Significado |
| **Carrossel de Destaque** | Termos marcados para exibição em destaque na home |
| **Moderação de Conteúdo** | Fluxo submissão → revisão → aprovação por perfil de usuário |

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **Backend** | Python 3.11 + Django 5.x |
| **Frontend** | Tailwind CSS, Alpine.js, HTMX |
| **Banco de Dados** | PostgreSQL 15 |
| **Containerização** | Docker + Docker Compose |
| **Servidor WSGI** | Gunicorn + gevent |
| **Proxy / Tunnel** | Traefik v2 + Cloudflare Tunnel |
| **Automação** | [just](https://github.com/casey/just) |

## Estrutura do Projeto

```
sinalize/
├── config/
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── catalog/                  # App principal
├── scripts/
│   └── entrypoint.sh
├── requirements/
│   ├── base.txt
│   ├── production.txt
│   └── development.txt
├── dotenv_files/
│   └── .env
├── data/
│   ├── postgres/
│   └── web/
│       ├── static/
│       └── media/
├── docker-compose.yml        # Desenvolvimento
├── docker-compose.prod.yml   # Produção
└── justfile
```

A infraestrutura de proxy fica separada do projeto:

```
infra/
├── docker-compose.yml        # Traefik + cloudflared
└── traefik/
    └── traefik.yml
```

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) Engine 24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+
- [just](https://github.com/casey/just#installation)

## Instalação e Configuração

Clone o repositório e configure as variáveis de ambiente:

```bash
git clone https://github.com/seu-usuario/sinalize.git
cd sinalize
cp dotenv_files/.env.example dotenv_files/.env
```

Edite o `.env` com suas configurações:

```dotenv
DEPLOY_MODE=dev
DEBUG=True
SECRET_KEY=troque-por-uma-chave-segura

POSTGRES_DB=sinalize_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_aqui

DB_NAME=sinalize_db
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_HOST=psql
DB_PORT=5432

LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo
ALLOWED_HOSTS=localhost,127.0.0.1
```

O arquivo `.env` nunca deve ser commitado — já está no `.gitignore`.

## Executando o Projeto

**Desenvolvimento:**
```bash
just up
```

O `entrypoint.sh` cuida do restante: aguarda o banco, roda `migrate`, compila o Tailwind, executa `collectstatic` e inicia o servidor. Acesse em `http://localhost:8000`.

**Produção:**
```bash
just up
just logs
```

O ambiente é detectado automaticamente pelo `DEPLOY_MODE=prod` no `.env`.

## Comandos (justfile)

**Docker**

| Comando | Descrição |
|---|---|
| `just up` | Sobe containers |
| `just build` | Rebuild do zero |
| `just restart` | Reinicia o Django |
| `just down-clean` | Derruba e apaga volumes |
| `just ps` | Lista containers |

**Django**

| Comando | Descrição |
|---|---|
| `just migrate` | Executa migrações |
| `just createsuperuser` | Cria superusuário |
| `just collectstatic` | Coleta arquivos estáticos |
| `just shell` | Shell interativo |

**Banco de Dados**

| Comando | Descrição |
|---|---|
| `just db` | Sessão interativa |
| `just resumo` | Contagem geral de registros |
| `just termos-status` | Status dos termos |
| `just fila-moderacao` | Pendentes de revisão |
| `just hierarquia-completa` | Mapa categoria → subcategoria → termo |
| `just backup` | Gera backup `.sql` com timestamp |

**Debug**

| Comando | Descrição |
|---|---|
| `just debug-on` | Ativa DEBUG e reinicia |
| `just debug-off` | Desativa DEBUG e reinicia |
| `just debug-status` | Exibe valor atual de DEBUG |

## Configuração de Produção

### Gunicorn + gevent

O projeto usa `gevent` para suportar múltiplas conexões simultâneas sem bloquear workers em downloads de vídeo:

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class gevent \
  --worker-connections 100 \
  --timeout 60
```

Fórmula para workers: `(2 × núcleos) + 1`. O projeto usa 4 por ser ambiente de pesquisa.

### Infraestrutura de Proxy

O roteamento externo é gerenciado por **Traefik v2** e **cloudflared**, declarados em `infra/docker-compose.yml` — separados do app para facilitar ajustes de hospedagem sem tocar no projeto.

O Traefik lê os `labels` dos containers e roteia automaticamente via rede compartilhada `proxy-net`. O cloudflared expõe o servidor à internet via Cloudflare Tunnel, sem abrir portas no roteador.

```bash
cd infra
docker compose up -d
docker logs traefik --tail=50
```

A rede `proxy-net` é criada pela infra e referenciada como `external: true` no compose do projeto.

### Conversão de Vídeo

Vídeos enviados são salvos no formato original com `status=PENDING`. A conversão para `.MP4` acontece fora do request HTTP:

```bash
docker compose exec projeto python manage.py convert_videos

# Agendar via cron (exemplo: todo dia às 3h)
0 3 * * * docker compose exec -T projeto python manage.py convert_videos
```

### Arquivos de Mídia

Para escalar o serving de mídia sem adicionar infraestrutura, crie uma Cache Rule na Cloudflare:

Dashboard → seu domínio → **Rules → Cache Rules → Create rule**
- Expression: `http.request.uri.path wildcard "/media/*"`
- Cache status: `Eligible for cache`

## Testando o Sistema

```bash
just ps                  # Containers rodando
just resumo              # Contagens do banco
just createsuperuser     # Criar admin
just criar-dominio-turismo  # Inserir dados iniciais
just termos-orfaos       # Deve retornar zero linhas
just termos-sem-dominio  # Deve retornar zero linhas
```

Acesse `http://localhost:8000/admin` para validar o painel.

## Estrutura do Banco de Dados

```
Domínio (ex: Turismo)
  └── Termo (ex: Hospedagem)
        └── Subcategoria (ex: Meios de Hospedagem)
              └── Categoria (ex: Infraestrutura)

Termo
  └── Vídeos (tipo: Sinal | Datilologia | Significado)
```

## Licença

Projeto acadêmico desenvolvido no **Instituto Federal Catarinense — Campus Camboriú**.
Vinculado ao Edital PIBITI nº 110/2023 — IFC/CNPq.
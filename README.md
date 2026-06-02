# Sinalize — Plataforma Web de Sinalário em LIBRAS

> Repositório sistematizado de sinais em Língua Brasileira de Sinais (LIBRAS), desenvolvido como plataforma web acessível para a comunidade surda, estudantes, professores e tradutores.

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Recursos Principais](#recursos-principais)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Executando o Projeto](#executando-o-projeto)
- [Comandos de Desenvolvimento (justfile)](#comandos-de-desenvolvimento-justfile)
- [Ambientes: Dev e Produção](#ambientes-dev-e-produção)
- [Testando o Sistema](#testando-o-sistema)
- [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
- [Licença](#licença)

---

## Sobre o Projeto

O **Sinalize** é uma aplicação web desenvolvida para organizar, buscar e disponibilizar sinais em LIBRAS, reduzindo barreiras comunicacionais por meio de um repositório visual e multimodal da língua.

O sistema funciona como um **sinalário digital**: associa termos da língua oral a registros visuais em vídeo, organizados em uma hierarquia de domínios, categorias e subcategorias.

O projeto está vinculado ao **Edital PIBITI nº 110/2023 do IFC/CNPq** e foca inicialmente no domínio de **Turismo**, com 70 sinais cadastrados para atender à demanda da região litorânea de Santa Catarina.

---

## Recursos Principais

| Recurso | Descrição |
|---|---|
| **Categorização Hierárquica** | Organização em domínios → categorias → subcategorias |
| **Flexibilidade Relacional** | Um mesmo termo pode pertencer a múltiplos contextos (ex: "Hospedagem" em Turismo e Atendimento) |
| **Busca Viva (HTMX)** | Filtro *as-you-type* sem recarregamento de página |
| **Acessibilidade WCAG 2.1 AAA** | Alto contraste, navegação por teclado, *skip links* e hierarquia visual clara |
| **Gestão Multimodal de Vídeos** | Classificação por tipo: Sinal, Datilologia (soletração manual) e Significado |
| **Carrossel de Destaque** | Termos marcados para exibição em destaque na página inicial |
| **Moderação de Conteúdo** | Fluxo de submissão → revisão → aprovação com controle por perfil de usuário |

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| **Backend** | Python 3.11 + Django 5.x |
| **Frontend** | Tailwind CSS, Alpine.js, HTMX |
| **Banco de Dados** | PostgreSQL 15 |
| **Containerização** | Docker + Docker Compose |
| **Tunnel / Proxy** | Cloudflare Tunnel (produção) |
| **Automação de tarefas** | [just](https://github.com/casey/just) |

---

## Estrutura do Projeto

```
sinalize/
├── config/
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── catalog/                  # App principal (termos, vídeos, categorias)
├── scripts/
│   └── entrypoint.sh         # Init: aguarda DB, migrate, collectstatic, runserver
├── dotenv_files/
│   └── .env                  # Variáveis de ambiente (não versionar)
├── data/
│   ├── postgres/             # Volume persistente do banco
│   └── web/
│       ├── static/
│       └── media/
├── docker-compose.yml        # Ambiente de desenvolvimento
├── docker-compose.prod.yml   # Ambiente de produção
└── justfile                  # Comandos de automação
```

---

## Pré-requisitos

Antes de clonar, certifique-se de ter instalado:

- [Docker](https://docs.docker.com/get-docker/) (Engine 24+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)
- [just](https://github.com/casey/just#installation) — gerenciador de comandos

```bash
# Verificar instalações
docker --version
docker compose version
just --version
```

---

## Instalação e Configuração

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/sinalize.git
cd sinalize
```

### 2. Configurar variáveis de ambiente

Crie o arquivo de variáveis a partir do exemplo fornecido:

```bash
cp dotenv_files/.env.example dotenv_files/.env
```

Edite `dotenv_files/.env` com suas configurações. Os campos obrigatórios são:

```dotenv
# ── Modo de deploy ────────────────────────────────────
DEPLOY_MODE=dev           # Trocar para 'prod' em produção
DEBUG=True                # Trocar para 'False' em produção
SECRET_KEY=troque-por-uma-chave-segura

# ── Banco de dados ────────────────────────────────────
POSTGRES_DB=sinalize_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_aqui

DB_NAME=sinalize_db
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_HOST=psql
DB_PORT=5432

# ── Django ────────────────────────────────────────────
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo
ALLOWED_HOSTS=localhost,127.0.0.1
```

> **Atenção:** o arquivo `.env` nunca deve ser commitado no repositório. Ele já está no `.gitignore`.

---

## Executando o Projeto

### Desenvolvimento

```bash
just up
```

Esse comando sobe os containers e executa as migrações automaticamente. O script `entrypoint.sh` cuida do resto: aguarda o banco estar pronto, roda `migrate`, compila o CSS do Tailwind, executa `collectstatic` e inicia o servidor Django.

Acesse em: **http://localhost:8000**

### Produção

Em produção, o ambiente é detectado automaticamente pelo `DEPLOY_MODE=prod` no `.env`. Os comandos `just` funcionam da mesma forma, mas passam a usar `docker-compose.prod.yml` e as credenciais corretas do banco.

```bash
just up          # Sobe produção
just logs        # Acompanha logs do Django
just logs-tunnel # Acompanha logs do túnel Cloudflare
```

---

## Comandos de Desenvolvimento (justfile)

O projeto usa `just` para centralizar todos os comandos. Para ver a lista completa:

```bash
just
```

Para inspecionar qual ambiente está ativo:

```bash
just env-info
```

### Docker

| Comando | Descrição |
|---|---|
| `just up` | Sobe containers e aplica migrações |
| `just build` | Rebuild do zero |
| `just restart` | Reinicia só o Django |
| `just down-clean` | Derruba e apaga todos os volumes |
| `just ps` | Lista containers em execução |

### Logs

| Comando | Descrição |
|---|---|
| `just logs` | Logs do Django em tempo real |
| `just logs-tail` | Últimas 50 linhas do Django |
| `just logs-tunnel` | Logs do túnel Cloudflare em tempo real |
| `just logs-all` | Logs de todos os serviços |

### Django

| Comando | Descrição |
|---|---|
| `just migrate` | Executa as migrações |
| `just createsuperuser` | Cria superusuário admin |
| `just collectstatic` | Coleta arquivos estáticos |
| `just shell` | Shell interativo do Django |
| `just check-db` | Verifica conexão com o banco |

### Debug

| Comando | Descrição |
|---|---|
| `just debug-on` | Ativa `DEBUG=True` e reinicia |
| `just debug-off` | Volta para `DEBUG=False` e reinicia |
| `just debug-status` | Exibe o valor atual de DEBUG |
| `just ver-entrypoint` | Exibe o conteúdo do `entrypoint.sh` |
| `just ver-env` | Lista variáveis de ambiente do container |

### Banco de Dados

| Comando | Descrição |
|---|---|
| `just db` | Sessão interativa no banco |
| `just resumo` | Contagem geral de registros |
| `just usuarios` | Lista usuários e permissões |
| `just termos-status` | Status dos termos cadastrados |
| `just fila-moderacao` | Termos e vídeos pendentes de revisão |
| `just hierarquia-completa` | Mapa completo de categoria → subcategoria → termo |
| `just backup` | Gera backup `.sql` com timestamp |

---

## Ambientes: Dev e Produção

O justfile detecta o ambiente automaticamente lendo `DEPLOY_MODE` do seu `.env`:

| `DEPLOY_MODE` | Compose usado | Usuário do banco | Banco |
|---|---|---|---|
| `dev` | `docker-compose.yml` | `postgres` | `sinalize_db` |
| `prod` | `docker-compose.prod.yml` | `sinalize_admin` | `sinalize_prod_db` |

Você também pode **forçar o ambiente** em qualquer comando:

```bash
ENV=prod just resumo    # Roda em contexto de produção
ENV=dev  just resumo    # Roda em contexto de desenvolvimento
```

---

## Testando o Sistema

Após subir o projeto com `just up`, siga o fluxo abaixo para validar o funcionamento:

### 1. Verificar que os containers estão rodando

```bash
just ps
```

Todos os serviços (`projeto`, `psql`, e em prod `cloudflare-tunnel`) devem estar `Up`.

### 2. Verificar o banco

```bash
just resumo
```

Deve retornar uma tabela com contagens (zeradas em instalação limpa).

### 3. Criar o superusuário

```bash
just createsuperuser
```

### 4. Acessar o painel administrativo

Acesse `http://localhost:8000/admin` e faça login com as credenciais criadas.

### 5. Inserir domínio inicial (Turismo)

```bash
just criar-dominio-turismo
```

### 6. Verificar integridade dos dados

```bash
just termos-orfaos       # Termos sem categoria
just termos-sem-dominio  # Termos sem domínio
```

Ambos devem retornar zero linhas em uma instalação limpa.

---

## Estrutura do Banco de Dados

O modelo de dados é hierárquico e relacional, permitindo que um termo pertença a múltiplos contextos:

```
Domínio (ex: Turismo)
  └── Pertence
        └── Termo (ex: Hospedagem)
              └── Classificação
                    └── Subcategoria (ex: Meios de Hospedagem)
                          └── Categoria (ex: Infraestrutura)

Termo
  └── Vídeos (tipo: Sinal | Datilologia | Significado)
```

Para visualizar a hierarquia completa dos dados cadastrados:

```bash
just hierarquia-completa
```

---

## Licença

Projeto acadêmico desenvolvido no **Instituto Federal Catarinense — Campus Camboriú**.  
Vinculado ao Edital PIBITI nº 110/2023 — IFC/CNPq.

---

*Desenvolvido com 🤟 para a comunidade surda.*

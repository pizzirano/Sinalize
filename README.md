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
- [Configuração do Servidor de Produção](#configuração-do-servidor-de-produção)
- [Monitoramento de Acessos](#monitoramento-de-acessos)
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
| **Servidor WSGI** | Gunicorn + gevent (worker assíncrono) |
| **Tunnel / Proxy** | Cloudflare Tunnel — serviço do sistema Ubuntu (não Docker) |
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
│   └── entrypoint.sh         # Init: aguarda DB, migrate, collectstatic, gunicorn
├── requirements/
│   ├── base.txt              # Dependências comuns
│   ├── production.txt        # gunicorn, whitenoise, gevent
│   └── development.txt
├── cloudflare/
│   ├── config.yml            # Configuração do tunnel (referência)
│   └── tunnel-credentials.json
├── dotenv_files/
│   └── .env                  # Variáveis de ambiente (não versionar)
├── data/
│   ├── postgres/             # Volume persistente do banco
│   └── web/
│       ├── static/
│       └── media/
├── docker-compose.yml        # Ambiente de desenvolvimento
├── docker-compose.prod.yml   # Ambiente de produção (sem cloudflared)
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

## Configuração do Servidor de Produção

Esta seção documenta as decisões técnicas tomadas para estabilizar o ambiente de produção sob acesso simultâneo de múltiplos usuários.

### Gunicorn: workers e classe assíncrona

O projeto usa **4 workers com worker class `gevent`** em produção. Essa configuração está em `scripts/entrypoint.sh`:

```bash
exec /venv/bin/gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class gevent \
  --worker-connections 100 \
  --timeout 60 \
  --access-logfile=-
```

**Por que gevent em vez do worker síncrono padrão?**

O worker padrão (`sync`) do Gunicorn processa uma requisição por vez por worker. Quando o servidor entrega arquivos de mídia pesados (vídeos `.MOV` de vídeos em LIBRAS), o worker fica bloqueado durante todo o download — nenhuma outra requisição consegue ser atendida por aquele worker nesse período. Com apenas 2 workers síncronos e múltiplos usuários simultâneos, isso gera erros 502 Bad Gateway.

O worker `gevent` é assíncrono por I/O: enquanto aguarda o envio de um arquivo grande, o mesmo worker atende outras requisições em paralelo. Cada worker consegue lidar com até 100 conexões simultâneas (`--worker-connections 100`) sem bloquear.

**Opções de worker disponíveis:**

| Worker | Quando usar | Dependência |
|---|---|---|
| `sync` (padrão) | Aplicações simples, sem I/O pesado | nenhuma |
| `gevent` | I/O pesado, arquivos de mídia, muitos usuários simultâneos | `pip install gevent` |
| `gthread` | Alternativa thread-based ao gevent | nenhuma extra |
| `uvicorn.workers.UvicornWorker` | Apps ASGI (Django Channels, FastAPI) | `pip install uvicorn` |

> O projeto **não usa Redis, Celery ou BullMQ**. O gevent resolve o problema de concorrência sem adicionar infraestrutura de filas.

**Fórmula recomendada para número de workers:**

```
workers = (2 × núcleos_de_CPU) + 1
```

Para um servidor com 2 núcleos: `(2 × 2) + 1 = 5 workers`. O projeto usa 4 por ser um ambiente de teste/pesquisa com recursos limitados.

---

### Cloudflare Tunnel: arquitetura correta

O projeto usa Cloudflare Tunnel para expor o servidor local à internet sem abrir portas no roteador ou contratar IP fixo. **O tunnel roda como serviço do sistema Ubuntu — não como container Docker.**

**Por que não rodar o cloudflared dentro do Docker?**

Rodar `cloudflared` dentro do Docker e também como serviço do sistema cria dois processos concorrendo pelo mesmo tunnel, causando falhas intermitentes de conexão (502). A decisão foi manter apenas o serviço do sistema, removendo o container `cloudflare-tunnel` do `docker-compose.prod.yml`.

**Configuração do tunnel (`/etc/cloudflared/config.yml`):**

```yaml
tunnel: SEU_TUNNEL_ID
credentials-file: /etc/cloudflared/tunnel-credentials.json

ingress:
  - hostname: seu-dominio.com
    service: http://localhost:8000
    originRequest:
      http2Origin: true
      noTLSVerify: true
  - service: http_status:404
```

- `http2Origin: true` — usa HTTP/2 entre o tunnel e o Gunicorn, reduzindo latência e melhorando estabilidade sob carga
- `noTLSVerify: true` — necessário porque a conexão interna (`localhost:8000`) não usa TLS

**Gerenciamento do serviço:**

```bash
# Ver status
sudo systemctl status cloudflared

# Reiniciar após alterar o config.yml
sudo systemctl restart cloudflared

# Ver logs em tempo real
sudo journalctl -u cloudflared -f

# Habilitar na inicialização do sistema
sudo systemctl enable cloudflared
```

> **Atenção:** após qualquer alteração em `/etc/cloudflared/config.yml`, execute `sudo systemctl restart cloudflared` para aplicar.

---

### Arquivos de mídia em produção

O Gunicorn não é otimizado para servir arquivos estáticos ou de mídia diretamente — cada arquivo entregue ocupa um worker durante o download. Para o estágio atual do projeto isso é aceitável, mas para escalar existem duas opções:

**Opção 1 — Cache na Cloudflare (sem custo, recomendada a curto prazo):**

No painel da Cloudflare, crie uma Cache Rule para o path `/media/*`. A Cloudflare passa a entregar os vídeos do edge sem tocar no Gunicorn após o primeiro acesso.

Dashboard → seu domínio → **Rules → Cache Rules → Create rule**
- Expression: `http.request.uri.path wildcard "/media/*"`
- Cache status: `Eligible for cache`

**Opção 2 — Storage externo (recomendada para produção definitiva):**

Migrar os arquivos de mídia para Cloudflare R2 ou AWS S3 e configurar o Django para usar o storage externo via `django-storages`. Os vídeos passam a ser servidos diretamente pelo CDN, sem passar pelo servidor.

---

## Monitoramento de Acessos

Para acompanhar os acessos em tempo real no terminal com colunas organizadas:

```bash
docker compose -f docker-compose.prod.yml logs projeto -f --tail=50 \
  | grep --line-buffered -E '"GET |"POST ' \
  | awk '
BEGIN {
  printf "\033[1;37m%-10s %-6s %-45s %-5s %-8s\033[0m\n", "HORA", "MÉTODO", "ROTA", "ST", "TAMANHO"
  printf "%s\n", "─────────────────────────────────────────────────────────────────────────────"
}
{
  for(i=1;i<=NF;i++) {
    if ($i ~ /^\[/) { split($i, t, ":"); hora = t[2]":"t[3]":"t[4] }
    if ($i ~ /^"(GET|POST)/) { metodo = substr($i,2); rota = $(i+1) }
    if ($i ~ /^[0-9]{3}$/) { status = $i; tamanho = $(i+1) }
  }
  cor = "\033[0m"
  if (status ~ /^2/) cor = "\033[32m"
  else if (status ~ /^3/) cor = "\033[33m"
  else if (status ~ /^4/) cor = "\033[31m"
  else if (status ~ /^5/) cor = "\033[1;31m"
  printf cor"%-10s %-6s %-45s %-5s %-8s\033[0m\n", hora, metodo, rota, status, tamanho
  fflush()
}'
```

Cores: verde = 2xx, amarelo = 3xx, vermelho = 4xx/5xx. `Ctrl+C` para sair.

> **Observação:** o IP exibido nos logs (`172.18.0.1`) é o gateway interno do Docker, não o IP real do usuário. O IP real é enviado pelo Cloudflare no header `CF-Connecting-IP` e pode ser capturado configurando o `--access-logformat` do Gunicorn para incluir esse header.

---

## Testando o Sistema

Após subir o projeto com `just up`, siga o fluxo abaixo para validar o funcionamento:

### 1. Verificar que os containers estão rodando

```bash
just ps
```

Em produção, apenas `projeto` e `psql` devem aparecer (o tunnel roda fora do Docker).

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

*Desenvolvido com apoio do Instituto Federal Catarinense - Campus Camboriú SC

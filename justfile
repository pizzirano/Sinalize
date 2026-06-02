# =============================================================================
# SINALIZE - COMANDOS DE DESENVOLVIMENTO E PRODUÇÃO
# =============================================================================
#
# O ambiente é detectado automaticamente pelo DEPLOY_MODE no dotenv_files/.env
#   DEPLOY_MODE=prod  → usa docker-compose.prod.yml + sinalize_admin + sinalize_prod_db
#   DEPLOY_MODE=dev   → usa docker-compose.yml      + postgres       + sinalize_db
#
# Você também pode forçar o ambiente na chamada:
#   ENV=prod just resumo
#   ENV=dev  just resumo
#
# =============================================================================

set shell := ["bash", "-cu"]

# ─── DETECÇÃO AUTOMÁTICA DE AMBIENTE ─────────────────────────────────────────

# Lê DEPLOY_MODE do .env, com fallback para 'dev'
DEPLOY_MODE := `grep -E '^DEPLOY_MODE=' dotenv_files/.env 2>/dev/null | cut -d= -f2 | tr -d '[:space:]' || echo "dev"`

# ENV pode ser forçado via linha de comando: ENV=prod just <cmd>
ENV := env_var_or_default("ENV", DEPLOY_MODE)

# ─── VARIÁVEIS POR AMBIENTE ──────────────────────────────────────────────────

# Arquivo compose
COMPOSE_FILE := if ENV == "prod" { "docker-compose.prod.yml" } else { "docker-compose.yml" }
COMPOSE      := "docker compose -f " + COMPOSE_FILE

# Container do Django
PROJETO_CTR  := "sinalize-projeto-1"

# Credenciais do banco (diferem por ambiente)
PSQL_CTR     := "sinalize-psql-1"
PSQL_USER    := if ENV == "prod" { "sinalize_admin" } else { "postgres" }
PSQL_DB      := if ENV == "prod" { "sinalize_prod_db" } else { "sinalize_db" }

# Atalho para psql não-interativo
PSQL_CMD     := "docker exec " + PSQL_CTR + " psql -U " + PSQL_USER + " -d " + PSQL_DB

# Atalho para psql interativo
PSQL_IT      := "docker exec -it " + PSQL_CTR + " psql -U " + PSQL_USER + " -d " + PSQL_DB

# =============================================================================
# AJUDA
# =============================================================================

# Lista todos os comandos disponíveis (padrão ao digitar apenas 'just')
default:
    @echo "Ambiente detectado: {{ ENV }} (compose: {{ COMPOSE_FILE }})"
    @echo ""
    @just --list --unsorted

# Mostra qual ambiente está ativo e as variáveis resolvidas
env-info:
    @echo "┌─────────────────────────────────────────┐"
    @echo "│          AMBIENTE: {{ ENV }}                    │"
    @echo "├─────────────────────────────────────────┤"
    @echo "│  Compose file : {{ COMPOSE_FILE }}"
    @echo "│  Projeto ctr  : {{ PROJETO_CTR }}"
    @echo "│  Psql ctr     : {{ PSQL_CTR }}"
    @echo "│  Psql user    : {{ PSQL_USER }}"
    @echo "│  Psql db      : {{ PSQL_DB }}"
    @echo "└─────────────────────────────────────────┘"

# =============================================================================
# DOCKER
# =============================================================================

# Sobe os containers e aplica as migrações automaticamente
up:
    {{COMPOSE}} up -d
    just migrate

# Faz o build dos containers do zero
build:
    {{COMPOSE}} up -d --build

# Reinicia o container do Django (sem derrubar tudo)
restart:
    {{COMPOSE}} restart projeto

# Derruba os containers e apaga todos os volumes (CUIDADO: apaga dados)
down-clean:
    {{COMPOSE}} down -v

# Mostra os logs do Django em tempo real
logs:
    {{COMPOSE}} logs -f projeto

# Mostra os logs do túnel Cloudflared em tempo real
logs-tunnel:
    docker logs -f sinalize-cloudflare-tunnel-1

# Mostra os logs de todos os serviços em tempo real
logs-all:
    {{COMPOSE}} logs -f

# Lista os containers em execução com status
ps:
    {{COMPOSE}} ps

# =============================================================================
# DJANGO
# =============================================================================

# Executa as migrações do Django
migrate:
    docker exec {{PROJETO_CTR}} python manage.py migrate

# Cria um superusuário administrador
createsuperuser:
    docker exec -it {{PROJETO_CTR}} python manage.py createsuperuser

# Coleta arquivos estáticos (útil em prod)
collectstatic:
    docker exec {{PROJETO_CTR}} python manage.py collectstatic --noinput

# Abre o shell interativo do Django (ótimo para testar ORM rápido)
shell:
    docker exec -it {{PROJETO_CTR}} python manage.py shell

# Exibe as configurações Django ativas (settings module em uso)
settings-info:
    docker exec {{PROJETO_CTR}} python manage.py diffsettings

# Ativa DEBUG=True no .env e reinicia o projeto (apenas prod, use com cuidado)
debug-on:
    @echo "⚠️  Ativando DEBUG=True em dotenv_files/.env"
    sed -i 's/^DEBUG=.*/DEBUG=True/' dotenv_files/.env
    {{COMPOSE}} restart projeto
    @echo "✅  DEBUG=True — lembre de desativar com: just debug-off"

# Desativa DEBUG=False no .env e reinicia o projeto
debug-off:
    @echo "🔒 Desativando DEBUG — voltando para False"
    sed -i 's/^DEBUG=.*/DEBUG=False/' dotenv_files/.env
    {{COMPOSE}} restart projeto
    @echo "✅  DEBUG=False — produção segura"

# Mostra o valor atual de DEBUG no .env
debug-status:
    @grep '^DEBUG=' dotenv_files/.env

# =============================================================================
# BANCO
# =============================================================================

# Entra direto no banco de dados (sessão interativa)
db:
    {{PSQL_IT}}

# Exibe um resumo geral com contagem de registros principais
resumo:
    {{PSQL_CMD}} -c "SELECT (SELECT COUNT(*) FROM auth_user) usuarios,(SELECT COUNT(*) FROM catalog_termo) termos,(SELECT COUNT(*) FROM catalog_video) videos,(SELECT COUNT(*) FROM catalog_categoria) categorias,(SELECT COUNT(*) FROM catalog_subcategoria) subcategorias,(SELECT COUNT(*) FROM catalog_dominio) dominios;"

# =============================================================================
# USUÁRIOS
# =============================================================================

# Lista todos os usuários, indicando permissões
usuarios:
    {{PSQL_CMD}} -c "SELECT id, username, email, is_staff, is_superuser FROM auth_user ORDER BY id;"

# Lista perfis de usuários e seus papéis
usuarios-perfis:
    {{PSQL_CMD}} -c "SELECT p.id, u.username, p.role FROM catalog_profile p JOIN auth_user u ON u.id = p.user_id ORDER BY p.id;"

# =============================================================================
# TERMOS
# =============================================================================

# Lista status dos termos mais recentes
termos-status:
    {{PSQL_CMD}} -c "SELECT id_termo, nome_termo, status, created_by_id FROM catalog_termo ORDER BY id_termo DESC;"

# Lista submissões com nome do usuário
submissoes:
    {{PSQL_CMD}} -c "SELECT u.username, t.id_termo, t.nome_termo, t.status FROM catalog_termo t LEFT JOIN auth_user u ON u.id = t.created_by_id ORDER BY t.id_termo DESC;"

# Lista catálogo público aprovado
catalogo-publico:
    {{PSQL_CMD}} -c "SELECT id_termo, nome_termo, status FROM catalog_termo WHERE status='APPROVED';"

# =============================================================================
# VÍDEOS
# =============================================================================

# Mostra últimos vídeos cadastrados
ver-videos:
    {{PSQL_CMD}} -c "SELECT id_video, titulo, status FROM catalog_video ORDER BY id_video DESC LIMIT 10;"

# Status dos vídeos e conversão
videos-status:
    {{PSQL_CMD}} -c "SELECT id_video, titulo, status, convertido FROM catalog_video ORDER BY id_video DESC;"

# Vídeos com autores
videos-autores:
    {{PSQL_CMD}} -c "SELECT v.id_video, v.titulo, u.username, v.status FROM catalog_video v LEFT JOIN auth_user u ON u.id = v.uploaded_by_id ORDER BY v.id_video DESC;"

# Vídeos para carrossel
ver-carrossel:
    {{PSQL_CMD}} -c "SELECT v.id_video, v.titulo, t.nome_termo, v.status FROM catalog_video v JOIN catalog_termo t ON t.id_termo = v.termo_id WHERE t.carrossel = true;"

# =============================================================================
# MODERAÇÃO
# =============================================================================

# Fila de moderação (termos + vídeos pendentes)
fila-moderacao:
    {{PSQL_CMD}} -c "SELECT 'TERMO' tipo,id_termo id,nome_termo nome,status FROM catalog_termo WHERE status='PENDING' UNION ALL SELECT 'VIDEO',id_video,titulo,status FROM catalog_video WHERE status='PENDING';"

# =============================================================================
# HIERARQUIA
# =============================================================================

# Mapa de categorias e subcategorias
categorias-mapa:
    {{PSQL_CMD}} -c "SELECT c.nome_categoria, s.nome_subcategoria FROM catalog_categoria c LEFT JOIN catalog_subcategoria s ON s.categoria_id = c.id_categoria ORDER BY c.nome_categoria;"

# Insere domínio Turismo caso não exista
criar-dominio-turismo:
    {{PSQL_CMD}} -c "INSERT INTO catalog_dominio (nome_dominio) SELECT 'Turismo' WHERE NOT EXISTS (SELECT 1 FROM catalog_dominio WHERE nome_dominio = 'Turismo');"

# Termos por domínio
dominios-termos:
    {{PSQL_CMD}} -c "SELECT d.nome_dominio, t.nome_termo FROM catalog_pertence p JOIN catalog_dominio d ON d.id_dominio = p.dominio_id JOIN catalog_termo t ON t.id_termo = p.termo_id ORDER BY d.nome_dominio;"

# Hierarquia completa do sistema
hierarquia-completa:
    {{PSQL_CMD}} -c "SELECT c.nome_categoria categoria, s.nome_subcategoria subcategoria, t.nome_termo termo, t.status FROM catalog_classificacao cl JOIN catalog_termo t ON t.id_termo = cl.termo_id JOIN catalog_subcategoria s ON s.id_subcategoria = cl.subcategoria_id JOIN catalog_categoria c ON c.id_categoria = s.categoria_id ORDER BY c.nome_categoria,s.nome_subcategoria,t.nome_termo;"

# =============================================================================
# INTEGRIDADE
# =============================================================================

# Termos sem classificação
termos-orfaos:
    {{PSQL_CMD}} -c "SELECT id_termo,nome_termo FROM catalog_termo t WHERE NOT EXISTS (SELECT 1 FROM catalog_classificacao c WHERE c.termo_id=t.id_termo);"

# Termos sem domínio
termos-sem-dominio:
    {{PSQL_CMD}} -c "SELECT id_termo,nome_termo FROM catalog_termo t WHERE NOT EXISTS (SELECT 1 FROM catalog_pertence p WHERE p.termo_id=t.id_termo);"

# =============================================================================
# DEBUG / INSPEÇÃO
# =============================================================================

# Exibe o conteúdo do entrypoint.sh
ver-entrypoint:
    cat ./scripts/entrypoint.sh

# Inspeciona variáveis de ambiente do container Django
ver-env:
    docker exec {{PROJETO_CTR}} env | sort

# Mostra as últimas 50 linhas de log do Django (sem seguir)
logs-tail:
    {{COMPOSE}} logs --tail=50 projeto

# Mostra as últimas 50 linhas do túnel Cloudflared (sem seguir)
logs-tunnel-tail:
    docker logs --tail=50 sinalize-cloudflare-tunnel-1

# Verifica conectividade do Django com o banco
check-db:
    docker exec {{PROJETO_CTR}} python manage.py check --database default

# =============================================================================
# LIMPEZA
# =============================================================================

# Limpa vídeos (CUIDADO: dados serão apagados)
limpar-videos:
    {{PSQL_CMD}} -c "TRUNCATE TABLE catalog_video RESTART IDENTITY CASCADE;"

# Reset parcial do sistema (termos, vídeos, classificações)
reset-sin15:
    {{PSQL_CMD}} -c "TRUNCATE TABLE catalog_video,catalog_classificacao,catalog_pertence,catalog_termo RESTART IDENTITY CASCADE;"

# Reset total do catálogo (CUIDADO: apaga tudo inclusive categorias e domínios)
reset-catalogo:
    {{PSQL_CMD}} -c "TRUNCATE TABLE catalog_video,catalog_classificacao,catalog_pertence,catalog_termo,catalog_subcategoria,catalog_categoria,catalog_dominio RESTART IDENTITY CASCADE;"

# =============================================================================
# BACKUP
# =============================================================================

# Gera backup completo do banco com timestamp
backup:
    docker exec -t {{PSQL_CTR}} pg_dump -U {{PSQL_USER}} -d {{PSQL_DB}} --clean --if-exists > backup_sinalize_$(date +%Y%m%d_%H%M%S).sql
    @echo "✅  Backup salvo em backup_sinalize_$(date +%Y%m%d_%H%M%S).sql"

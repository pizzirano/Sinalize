set shell := ["powershell", "-Command"]

# ===========================================================================
# SINALIZE - COMANDOS DE DESENVOLVIMENTO
# ===========================================================================

# Lista todos os comandos disponíveis (padrao ao digitar apenas 'just')
default:
    @just --list --unsorted

# ===========================================================================
# DOCKER
# ===========================================================================

# Sobe os containers e aplica as migracoes automaticamente
up:
    docker compose up -d
    just migrate

# Faz o build dos containers do zero
build:
    docker compose up -d --build

# Derruba os containers e apaga todos os volumes (limpeza de dados)
down-clean:
    docker compose down -v

# Mostra os logs do Django em tempo real
logs:
    docker compose logs -f projeto

# Mostra logs do Gunicorn com bind
logs-gunicorn:
    docker compose logs -f projeto | findstr "bind"

# Mostra todos os logs de erro
logs-errors:
    docker compose logs -f projeto | findstr "ERROR"

# ===========================================================================
# DJANGO
# ===========================================================================

# Executa as migracoes do Django
migrate:
    docker exec -it sinalize-web python manage.py migrate

# Cria um superusuario administrador
createsuperuser:
    docker exec -it sinalize-web python manage.py createsuperuser

# Abre o shell interativo do Django (otimo para testar ORM rapido)
shell:
    docker exec -it sinalize-web python manage.py shell

# ===========================================================================
# BANCO
# ===========================================================================

# Entra direto no banco de dados correto (sinalize_db)
db:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db

criar-dominio-turismo:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "INSERT INTO catalog_dominio (nome_dominio) SELECT 'Turismo' WHERE NOT EXISTS (SELECT 1 FROM catalog_dominio WHERE nome_dominio = 'Turismo');"

# Exibe um resumo geral com a contagem de registros em todas as tabelas principais
resumo:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT (SELECT COUNT(*) FROM auth_user) usuarios,(SELECT COUNT(*) FROM catalog_termo) termos,(SELECT COUNT(*) FROM catalog_video) videos,(SELECT COUNT(*) FROM catalog_categoria) categorias,(SELECT COUNT(*) FROM catalog_subcategoria) subcategorias,(SELECT COUNT(*) FROM catalog_dominio) dominios;"

# ===========================================================================
# USUARIOS
# ===========================================================================

# Lista todos os usuarios, indicando quem eh Administrador/Staff
usuarios:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT id, username, email, is_staff, is_superuser FROM auth_user ORDER BY id;"

# Lista os Perfis (Profiles) criados e vinculados aos usuarios
usuarios-perfis:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT p.id, u.username, p.role FROM catalog_profile p JOIN auth_user u ON u.id = p.user_id ORDER BY p.id;"

# ===========================================================================
# TERMOS
# ===========================================================================

# Mostra a listagem de termos ordenada pelos mais recentes e seus respectivos status
termos-status:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT id_termo, nome_termo, status, created_by_id FROM catalog_termo ORDER BY id_termo DESC;"

# Lista os termos enviados cruzando com o nome do usuario que os submeteu
submissoes:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT u.username, t.id_termo, t.nome_termo, t.status FROM catalog_termo t LEFT JOIN auth_user u ON u.id = t.created_by_id ORDER BY t.id_termo DESC;"

# Filtra e exibe apenas os termos que ja foram aprovados e estao publicos no catalogo
catalogo-publico:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT id_termo, nome_termo, status FROM catalog_termo WHERE status='APPROVED';"

# ===========================================================================
# VIDEOS
# ===========================================================================

# Mostra os ultimos 10 videos enviados e seus status de moderacao
ver-videos:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT id_video, titulo, status FROM catalog_video ORDER BY id_video DESC LIMIT 10;"

# Mostra o status de moderacao e conversao mp4 de todos os videos
videos-status:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT id_video, titulo, status, convertido FROM catalog_video ORDER BY id_video DESC;"

# Cruza os videos com os usuarios que fizeram o upload
videos-autores:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT v.id_video, v.titulo, u.username, v.status FROM catalog_video v LEFT JOIN auth_user u ON u.id = v.uploaded_by_id ORDER BY v.id_video DESC;"

# Lista todos os videos cujos termos estao marcados para exibicao no carrossel
ver-carrossel:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT v.id_video, v.titulo, t.nome_termo, v.status FROM catalog_video v JOIN catalog_termo t ON t.id_termo = v.termo_id WHERE t.carrossel = true;"

# ===========================================================================
# MODERACAO
# ===========================================================================

# Reune em uma unica fila tudo que esta 'PENDING' (Termos e Videos) esperando aprovacao
fila-moderacao:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT 'TERMO' tipo,id_termo id,nome_termo nome,status FROM catalog_termo WHERE status='PENDING' UNION ALL SELECT 'VIDEO',id_video,titulo,status FROM catalog_video WHERE status='PENDING';"

# ===========================================================================
# HIERARQUIA
# ===========================================================================

# Exibe a estrutura de Categorias e suas respectivas Subcategorias cadastradas
categorias-mapa:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT c.nome_categoria, s.nome_subcategoria FROM catalog_categoria c LEFT JOIN catalog_subcategoria s ON s.categoria_id = c.id_categoria ORDER BY c.nome_categoria;"

# Exibe o mapeamento de quais termos pertencem a quais grandes dominios de conhecimento
dominios-termos:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT d.nome_dominio, t.nome_termo FROM catalog_pertence p JOIN catalog_dominio d ON d.id_dominio = p.dominio_id JOIN catalog_termo t ON t.id_termo = p.termo_id ORDER BY d.nome_dominio;"

# Mostra a arvore genealogica completa: Categoria -> Subcategoria -> Termo cadastrado
hierarquia-completa:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT c.nome_categoria categoria, s.nome_subcategoria subcategoria, t.nome_termo termo, t.status FROM catalog_classificacao cl JOIN catalog_termo t ON t.id_termo = cl.termo_id JOIN catalog_subcategoria s ON s.id_subcategoria = cl.subcategoria_id JOIN catalog_categoria c ON c.id_categoria = s.categoria_id ORDER BY c.nome_categoria,s.nome_subcategoria,t.nome_termo;"

# ===========================================================================
# INTEGRIDADE
# ===========================================================================

# Procura por termos que ficaram salvos mas nao foram vinculados a nenhuma subcategoria
termos-orfaos:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT id_termo,nome_termo FROM catalog_termo t WHERE NOT EXISTS (SELECT 1 FROM catalog_classificacao c WHERE c.termo_id=t.id_termo);"

# Procura por termos que nao foram vinculados a nenhuma area/dominio tecnico
termos-sem-dominio:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "SELECT id_termo,nome_termo FROM catalog_termo t WHERE NOT EXISTS (SELECT 1 FROM catalog_pertence p WHERE p.termo_id=t.id_termo);"

# ===========================================================================
# LIMPEZA
# ===========================================================================

# Limpa a tabela de videos (CUIDADO: Use apenas para resetar testes locais!)
limpar-videos:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "TRUNCATE TABLE catalog_video RESTART IDENTITY CASCADE;"

# Reseta o banco apagando videos, classificacoes, termos e dependencias (Mantem categorias/estruturas base)
reset-sin15:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "TRUNCATE TABLE catalog_video,catalog_classificacao,catalog_pertence,catalog_termo RESTART IDENTITY CASCADE;"

# Limpa absolutamente TODO o catalogo (Zera o banco de dados inteiro mantendo apenas as tabelas vazias)
reset-catalogo:
    docker exec -it sinalize-db psql -U sinalize_admin -d sinalize_prod_db -c "TRUNCATE TABLE catalog_video,catalog_classificacao,catalog_pertence,catalog_termo,catalog_subcategoria,catalog_categoria,catalog_dominio RESTART IDENTITY CASCADE;"

# ===========================================================================
# BACKUP
# ===========================================================================

# Realiza o dump completo do banco salvando em arquivos .sql e .txt na pasta atual
backup:
    docker exec -t sinalize-db pg_dump -U sinalize_admin -d sinalize_prod_db --clean --if-exists > backup_sinalize.sql
    docker exec -t sinalize-db pg_dump -U sinalize_admin -d sinalize_prod_db --clean --if-exists > backup_sinalize.txt

# ===========================================================================
# TRAEFIK
# ===========================================================================

# Lista containers conectados ao proxy-net
traefik-rede:
    docker network inspect proxy-net

# Mostra labels Traefik da aplicacao
traefik-labels:
    docker inspect sinalize-web --format "{{{{json .Config.Labels}}}}"

# Mostra informacoes completas do container
traefik-inspect:
    docker inspect sinalize-web

# Verifica se o container esta na proxy-net
traefik-network:
    docker inspect sinalize-web --format "{{{{json .NetworkSettings.Networks}}}}"

# Testa resposta HTTP local do container
traefik-test:
    docker exec -it sinalize-web curl -I http://localhost:8000

# Verifica resolucao DNS dentro da rede docker
traefik-dns:
    docker exec -it sinalize-web getent hosts sinalize-web

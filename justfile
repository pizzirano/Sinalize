set shell := ["powershell", "-Command"]


# Justfile - Atalhos de comandos para o projeto Sinalize

# Lista todos os comandos disponíveis (padrão ao digitar apenas 'just')
default:
    @just --list

# Sobe os containers e aplica as migrações automaticamente
up:
    docker compose up -d
    @echo "Aguardando inicialização do banco..." && sleep 3
    just migrate

# Derruba os containers e apaga todos os volumes (limpeza de dados)
down-clean:
    docker compose down -v

# Faz o build dos containers do zero
build:
    docker compose up -d --build

# Executa as migrações do Django
migrate:
    docker exec -it sinalize-projeto-1 python manage.py migrate

# Cria um superusuário administrador
createsuperuser:
    docker exec -it sinalize-projeto-1 python manage.py createsuperuser

# Entra direto no banco de dados correto (sinalize_db)
db:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db

#  Mostra os logs do Django em tempo real
logs:
    docker compose logs -f projeto

# Lista todos os usuários cadastrados no sistema
ver-usuarios:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT id, username, email, is_superuser FROM auth_user;"
# Mostra os últimos 5 vídeos enviados e seus status de moderação
ver-videos:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT id_video, titulo, status FROM catalog_video ORDER BY id_video DESC LIMIT 5;"

# Limpa a tabela de vídeos (CUIDADO: Use apenas para resetar testes locais!)
limpar-videos:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "TRUNCATE TABLE catalog_video CASCADE;"

# =============================================================================
# INSPEÇÃO RÁPIDA DE DADOS (FLUXO SIN-15 & CATÁLOGO)
# =============================================================================

# Mostra o status de moderação de todos os vídeos (Pendente, Aprovado, Rejeitado)
videos-status:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT id_video, titulo, status, convertido FROM catalog_video ORDER BY id_video DESC;"

# Lista todos os usuários, indicando quem é Administrador/Staff
usuarios:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT id, username, email, is_staff, is_superuser FROM auth_user ORDER BY id ASC;"

# Cruza os vídeos com os usuários que fizeram o upload
videos-autores:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT v.id_video, v.titulo, u.username AS enviado_por, v.status FROM catalog_video v LEFT JOIN auth_user u ON v.uploaded_by_id = u.id;"

# Lista os Perfis (Profiles) criados e vinculados aos usuários
usuarios-perfis:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT p.id, u.username, p.feedback FROM catalog_profile p JOIN auth_user u ON p.user_id = u.id;"

# Exibe a estrutura de Categorias, Subcategorias e Termos cadastrados
categorias-mapa:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT c.nome AS categoria, s.nome AS subcategoria FROM catalog_categoria c LEFT JOIN catalog_subcategoria s ON s.categoria_id = c.id_categoria;"

# =============================================================================
# CONVENIÊNCIA E AMBIENTE DE TESTE
# =============================================================================

# Abre o shell interativo do Django (ótimo para testar ORM rápido)
shell:
    docker exec -it sinalize-projeto-1 python manage.py shell

# =============================================================================
# RELATÓRIOS E CONSULTAS DO MODELO DE NEGÓCIO
# =============================================================================

# Lista todos os vídeos cujos termos estão marcados para exibição no carrossel
ver-carrossel:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT v.id_video, v.titulo, t.nome_termo AS termo_no_carrossel, v.status FROM catalog_video v JOIN catalog_termo t ON v.termo_id = t.id_termo WHERE t.carrossel = true;"

# Exibe o mapeamento completo de quais categorias pertencem a quais domínios
dominios-categorias:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT d.nome_dominio AS dominio, c.nome_categoria AS categoria_relacionada FROM catalog_categoria c JOIN catalog_dominio d ON c.dominio_id = d.id_dominio ORDER BY d.nome_dominio;"

# Mostra a árvore genealógica completa: Categoria -> Subcategoria -> Termos associados
hierarquia-termos:
    docker exec -it sinalize-psql-1 psql -U postgres -d sinalize_db -c "SELECT c.nome_categoria AS categoria, s.nome_subcategoria AS subcategoria, t.nome_termo AS termo FROM catalog_classificacao cl JOIN catalog_termo t ON cl.termo_id = t.id_termo JOIN catalog_subcategoria s ON cl.subcategoria_id = s.id_subcategoria JOIN catalog_categoria c ON s.categoria_id = c.id_categoria ORDER BY c.nome_categoria, s.nome_subcategoria;"
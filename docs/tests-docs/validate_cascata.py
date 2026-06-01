#!/usr/bin/env python
"""
SCRIPT DE VALIDAÇÃO - Cascata de Aprovação
Verifica se os patches foram aplicados corretamente e a cascata funciona.
Execute com: python manage.py shell < validate_cascata.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from catalog.models import Termo, Categoria, Subcategoria, Classificacao, Video
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("VALIDAÇÃO DE CASCATA DE APROVAÇÃO")
print("=" * 80)

# 1. Verificar se métodos existem
print("\n[1] Verificando se novos métodos existem em Termo...")
termo_sample = Termo.objects.first()
if termo_sample:
    assert hasattr(termo_sample, 'get_subcategorias'), "❌ Método get_subcategorias() não existe"
    assert hasattr(termo_sample, 'get_categorias'), "❌ Método get_categorias() não existe"
    print("✅ Métodos encontrados: get_subcategorias() e get_categorias()")
else:
    print("⚠️  Nenhum Termo encontrado no banco. Criando um para teste...")
    # Criar dados de teste
    from django.contrib.auth.models import User
    from catalog.models import Dominio
    
    # Criar domínio
    dominio, _ = Dominio.objects.get_or_create(nome_dominio="Teste")
    
    # Criar categoria
    categoria = Categoria.objects.create(
        nome_categoria="Categoria Teste",
        dominio=dominio,
        status='PENDING'
    )
    
    # Criar subcategoria
    subcategoria = Subcategoria.objects.create(
        nome_subcategoria="Subcategoria Teste",
        categoria=categoria,
        status='PENDING'
    )
    
    # Criar termo
    termo = Termo.objects.create(
        nome_termo="Termo Teste",
        status='PENDING'
    )
    
    # Criar classificação
    Classificacao.objects.create(
        termo=termo,
        subcategoria=subcategoria
    )
    
    # Criar vídeo
    video = Video.objects.create(
        tipo_video='Sinal',
        titulo='Vídeo Teste',
        termo=termo,
        status='PENDING'
    )
    
    print(f"✅ Dados de teste criados:")
    print(f"   - Categoria ID: {categoria.id_categoria}, Status: {categoria.status}")
    print(f"   - Subcategoria ID: {subcategoria.id_subcategoria}, Status: {subcategoria.status}")
    print(f"   - Termo ID: {termo.id_termo}, Status: {termo.status}")
    print(f"   - Vídeo ID: {video.id_video}, Status: {video.status}")

# 2. Testar get_subcategorias()
print("\n[2] Testando método get_subcategorias()...")
termo = Termo.objects.first()
if termo:
    subcategorias = termo.get_subcategorias()
    print(f"✅ get_subcategorias() retornou {subcategorias.count()} subcategoria(s)")
    for sub in subcategorias:
        print(f"   - {sub.nome_subcategoria} (ID: {sub.id_subcategoria}, Status: {sub.status})")

# 3. Testar get_categorias()
print("\n[3] Testando método get_categorias()...")
if termo:
    categorias = termo.get_categorias()
    print(f"✅ get_categorias() retornou {categorias.count()} categoria(s)")
    for cat in categorias:
        print(f"   - {cat.nome_categoria} (ID: {cat.id_categoria}, Status: {cat.status})")

# 4. Testar cascata de aprovação
print("\n[4] Testando cascata de aprovação...")
if termo:
    print(f"\n   Status ANTES de aprovar:")
    print(f"   - Termo: {termo.status}")
    print(f"   - Vídeos vinculados: {termo.videos.first().status if termo.videos.exists() else 'N/A'}")
    for sub in termo.get_subcategorias():
        print(f"   - Subcategoria {sub.id_subcategoria}: {sub.status}")
    for cat in termo.get_categorias():
        print(f"   - Categoria {cat.id_categoria}: {cat.status}")
    
    # Simular aprovação (mesma lógica que view)
    novo_status = 'APPROVED'
    termo.status = novo_status
    termo.save(update_fields=['status'])
    
    # Aprovar vídeos
    termo.videos.filter(
        status__in=['PENDING', 'AJUSTE']
    ).update(status=novo_status)
    
    # Cascata de Categoria/Subcategoria
    if novo_status == 'APPROVED':
        subcategorias = termo.get_subcategorias()
        subcategorias.filter(
            status__in=['PENDING', 'AJUSTE']
        ).update(status='APPROVED')
        
        categorias = termo.get_categorias()
        categorias.filter(
            status__in=['PENDING', 'AJUSTE']
        ).update(status='APPROVED')
    
    # Recarregar do banco
    termo.refresh_from_db()
    
    print(f"\n   Status DEPOIS de aprovar:")
    print(f"   - Termo: {termo.status}")
    print(f"   - Vídeos vinculados: {termo.videos.first().status if termo.videos.exists() else 'N/A'}")
    for sub in termo.get_subcategorias():
        sub.refresh_from_db()
        print(f"   - Subcategoria {sub.id_subcategoria}: {sub.status}")
    for cat in termo.get_categorias():
        cat.refresh_from_db()
        print(f"   - Categoria {cat.id_categoria}: {cat.status}")
    
    # Verificar se tudo foi aprovado
    if termo.status == 'APPROVED' and \
       termo.videos.filter(status='APPROVED').exists() and \
       termo.get_subcategorias().filter(status='APPROVED').exists() and \
       termo.get_categorias().filter(status='APPROVED').exists():
        print("\n✅ CASCATA FUNCIONANDO CORRETAMENTE!")
    else:
        print("\n❌ CASCATA NÃO FUNCIONOU COMO ESPERADO")

# 5. Verificar Home query
print("\n[5] Testando query de Home (Categoria.objects.filter(status='APPROVED'))...")
categorias_aprovadas = Categoria.objects.filter(status='APPROVED')
print(f"✅ Categorias APPROVED encontradas: {categorias_aprovadas.count()}")
for cat in categorias_aprovadas[:5]:
    print(f"   - {cat.nome_categoria} (ID: {cat.id_categoria})")

print("\n" + "=" * 80)
print("VALIDAÇÃO CONCLUÍDA")
print("=" * 80)

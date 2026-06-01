# GUIA PRÁTICO DE TESTE - CASCATA DE APROVAÇÃO

## 🎯 Objetivo
Verificar que quando você aprova um Termo no painel de moderação, a Categoria e Subcategoria relacionadas são automaticamente aprovadas.

---

## 📋 PRÉ-REQUISITOS

- [ ] Django rodando (local ou Docker)
- [ ] Usuário Moderador logado
- [ ] Database com dados de teste (ou siga o script abaixo para criar)

---

## 🔧 PREPARAÇÃO (Se não tiver dados)

### Opção A: Criar dados via Django Shell

```bash
# Entrar no shell Django
python manage.py shell
# ou no Docker:
docker compose exec projeto python manage.py shell
```

```python
from catalog.models import Dominio, Categoria, Subcategoria, Classificacao, Termo, Video

# Criar domínio
dominio, _ = Dominio.objects.get_or_create(nome_dominio="Teste")

# Criar categoria PENDING
categoria = Categoria.objects.create(
    nome_categoria="Tecnologia",
    dominio=dominio,
    status='PENDING'
)
print(f"Categoria criada: ID={categoria.id_categoria}, Status=PENDING")

# Criar subcategoria PENDING
subcategoria = Subcategoria.objects.create(
    nome_subcategoria="Computadores",
    categoria=categoria,
    status='PENDING'
)
print(f"Subcategoria criada: ID={subcategoria.id_subcategoria}, Status=PENDING")

# Criar termo PENDING
termo = Termo.objects.create(
    nome_termo="Mouse",
    status='PENDING'
)
print(f"Termo criado: ID={termo.id_termo}, Status=PENDING")

# Relacionar termo à subcategoria
classificacao = Classificacao.objects.create(
    termo=termo,
    subcategoria=subcategoria
)
print(f"Classificação criada")

# Criar vídeo PENDING
video = Video.objects.create(
    tipo_video='Sinal',
    titulo='Vídeo do Mouse',
    termo=termo,
    status='PENDING'
)
print(f"Vídeo criado: ID={video.id_video}, Status=PENDING")

print("\n✅ Dados de teste criados com sucesso!")
exit()
```

### Opção B: Usar dados existentes
Se já houver submissões pendentes, use-as.

---

## 🧪 TESTE PASSO A PASSO

### Passo 1: Verificar Status ANTES

No Django Shell:
```python
from catalog.models import Termo, Categoria, Subcategoria

termo = Termo.objects.filter(nome_termo='Mouse').first()
if termo:
    print(f"ANTES DE APROVAR:")
    print(f"  Termo: {termo.nome_termo} - Status: {termo.status}")
    print(f"  Subcategoria(s): ")
    for sub in termo.get_subcategorias():
        print(f"    - {sub.nome_subcategoria} - Status: {sub.status}")
    print(f"  Categoria(s):")
    for cat in termo.get_categorias():
        print(f"    - {cat.nome_categoria} - Status: {cat.status}")
    print(f"  Vídeos:")
    for vid in termo.videos.all():
        print(f"    - {vid.titulo} - Status: {vid.status}")
else:
    print("Termo não encontrado")
```

**Resultado esperado**:
```
ANTES DE APROVAR:
  Termo: Mouse - Status: PENDING
  Subcategoria(s): 
    - Computadores - Status: PENDING
  Categoria(s):
    - Tecnologia - Status: PENDING
  Vídeos:
    - Vídeo do Mouse - Status: PENDING
```

---

### Passo 2: Acessar Painel de Moderação

1. Abrir navegador: `http://localhost:8000/catalog/moderacao/`
   (ou sua URL de produção)

2. Verificar que aparece o Termo "Mouse" na seção "Termos pendentes"

3. Localizar a seção de "Termos pendentes" e encontrar o card do termo

---

### Passo 3: Clicar em "Aprovar Termo e Vídeos"

1. Procurar pelo botão verde "✅ Aprovar termo e vídeos"
2. Clicar nele
3. Esperar a resposta do servidor (HTMX fará a requisição)
4. O card deve desaparecer da tela ou mudar de status

**O que acontece nos bastidores**:
- Requisição HTMX POST para `/catalog/moderacao/termo/{id}/aprovar/`
- Django processa com `moderation_action()`
- Cascata é executada automaticamente
- Resposta HTTP "" (vazio, só para HTMX atualizar)

---

### Passo 4: Verificar Status DEPOIS

No Django Shell:
```python
from catalog.models import Termo

termo = Termo.objects.filter(nome_termo='Mouse').first()
if termo:
    print(f"DEPOIS DE APROVAR:")
    print(f"  Termo: {termo.nome_termo} - Status: {termo.status}")
    print(f"  Subcategoria(s): ")
    for sub in termo.get_subcategorias():
        sub.refresh_from_db()  # Atualizar do banco
        print(f"    - {sub.nome_subcategoria} - Status: {sub.status}")
    print(f"  Categoria(s):")
    for cat in termo.get_categorias():
        cat.refresh_from_db()  # Atualizar do banco
        print(f"    - {cat.nome_categoria} - Status: {cat.status}")
    print(f"  Vídeos:")
    for vid in termo.videos.all():
        print(f"    - {vid.titulo} - Status: {vid.status}")
else:
    print("Termo não encontrado")
```

**Resultado esperado**:
```
DEPOIS DE APROVAR:
  Termo: Mouse - Status: APPROVED ✅
  Subcategoria(s): 
    - Computadores - Status: APPROVED ✅ [CASCATA]
  Categoria(s):
    - Tecnologia - Status: APPROVED ✅ [CASCATA]
  Vídeos:
    - Vídeo do Mouse - Status: APPROVED ✅
```

---

### Passo 5: Verificar Logs (Opcional)

Se quer ver a cascata sendo registrada:

```bash
# Terminal
tail -f /var/log/django.log | grep "Cascata"

# Esperado após clique de aprovação:
# INFO: Cascata: Termo 123 aprovado. Subcategorias: 1, Categorias: 1
```

---

### Passo 6: Verificar Home

1. Acessar `http://localhost:8000/catalog/home/`
2. Procurar pela galeria de categorias
3. Verificar se "Tecnologia" aparece (status APPROVED agora)

**Antes**: Categoria não aparecia (status PENDING)
**Depois**: ✅ Categoria aparece na galeria

---

## ✅ CHECKLIST DE VALIDAÇÃO

| Item | Esperado | Resultado |
|------|----------|-----------|
| Termo aprovado | APPROVED | ☐ |
| Vídeo aprovado | APPROVED | ☐ |
| Subcategoria aprovada (cascata) | APPROVED | ☐ |
| Categoria aprovada (cascata) | APPROVED | ☐ |
| Home exibe categoria | Sim | ☐ |
| Navegação funciona | Sem erro 404 | ☐ |
| Logs contêm "Cascata" | Sim | ☐ |

---

## 🐛 TROUBLESHOOTING

### Problema: Categoria/Subcategoria ainda PENDING após aprovar
**Solução**:
1. Verificar que `moderation_action()` foi modificada
   ```python
   # Deve conter:
   if novo_status == 'APPROVED':
       subcategorias = termo.get_subcategorias()
       ...
   ```
2. Reiniciar Django
3. Limpar cache do navegador (Ctrl+Shift+Del)

### Problema: "Cascata" não aparece em logs
**Solução**:
1. Verificar que logger.info() foi adicionado
2. Verificar nível de log (DEBUG ou INFO)
3. Verificar caminho do log_file

### Problema: KeyError: 'approvar' ao clicar botão
**Solução**:
1. Verificar que `action = action.strip().lower()` existe em moderation_action()
2. Isso normaliza 'APROVAR' → 'aprovar' para match no MAP

### Problema: Categoria/Subcategoria existem mas não são encontradas
**Solução**:
1. Verificar que `Classificacao` existe e relaciona Termo → Subcategoria
2. Executar:
   ```python
   termo = Termo.objects.get(id_termo=123)
   print(termo.get_subcategorias())  # Deve retornar QuerySet
   print(termo.get_categorias())     # Deve retornar QuerySet
   ```

---

## 📊 EXEMPLO REAL - TRACE COMPLETO

### Submissão inicial:
```
DB State:
  Categoria "Transporte" → ID=1, Status=PENDING
  ├─ Subcategoria "Ônibus" → ID=1, Status=PENDING
  │  └─ Classificacao → Termo ID=50
  │     └─ Termo "Ônibus" → ID=50, Status=PENDING
  │        └─ Video "Sinal" → ID=100, Status=PENDING
```

### Moderador clica "✅ Aprovar Termo":
```
POST /catalog/moderacao/termo/50/aprovar/
Headers: X-CSRFToken, HX-Request: true
```

### Django executa moderation_action():
```python
# 1. Busca Termo
termo = Termo.objects.get(id_termo=50)

# 2. Aprova Termo
termo.status = 'APPROVED'
termo.save()

# 3. Aprova Vídeos
termo.videos.update(status='APPROVED')

# 4. CASCATA: Aprova Subcategorias
subcategorias = termo.get_subcategorias()  # QuerySet com Subcategoria 1
subcategorias.filter(status__in=['PENDING', 'AJUSTE']).update(status='APPROVED')

# 5. CASCATA: Aprova Categorias
categorias = termo.get_categorias()  # QuerySet com Categoria 1
categorias.filter(status__in=['PENDING', 'AJUSTE']).update(status='APPROVED')

# 6. Log
logger.info("Cascata: Termo 50 aprovado. Subcategorias: 1, Categorias: 1")
```

### DB State após aprovação:
```
DB State:
  Categoria "Transporte" → ID=1, Status=APPROVED ✅ [CASCATA]
  ├─ Subcategoria "Ônibus" → ID=1, Status=APPROVED ✅ [CASCATA]
  │  └─ Classificacao → Termo ID=50
  │     └─ Termo "Ônibus" → ID=50, Status=APPROVED ✅
  │        └─ Video "Sinal" → ID=100, Status=APPROVED ✅
```

### Home query funciona:
```python
# views.py → home()
categorias = Categoria.objects.filter(status='APPROVED')

# Resultado antes: [] (vazio, erro 404)
# Resultado depois: [<Categoria: Transporte>] ✅
```

---

## 📝 NOTAS

1. **Idempotência**: Pode clicar múltiplas vezes no botão de aprovação
   - Primeira: Altera PENDING → APPROVED
   - Subsequentes: Já APPROVED, update() não faz nada

2. **Múltiplos termos por subcategoria**:
   - SubCategoria pode ter N termos
   - Quando aprova um, fica APPROVED
   - Quando aprova outro, update() não muda (já está APPROVED)
   - ✅ Seguro

3. **Rejeição/Ajuste não cascateia**:
   - Rejeitar Termo → Vídeos rejeitados, MAS Categoria/SubCategoria ficam PENDING
   - Isso permite workflow: rejeitar Termo, aprovar Categoria para futuro
   - ✅ Design correto

---

## ✨ SUCESSO!

Se todos os itens do checklist estão ✓, a cascata de aprovação está funcionando corretamente.

🎉 Pronto para produção!

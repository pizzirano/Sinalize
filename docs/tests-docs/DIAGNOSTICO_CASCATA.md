# DIAGNÓSTICO COMPLETO - SISTEMA DE MODERAÇÃO COM CASCATA DE APROVAÇÃO

## 📋 RESUMO EXECUTIVO

O problema raiz é a **falta de cascata de aprovação hierárquica**: quando um Termo é aprovado, sua Categoria e Subcategoria relacionadas não são automaticamente aprovadas, causando inconsistência no banco e erros nas views que filtram `status='APPROVED'`.

---

## 🔍 ANÁLISE ESTRUTURAL

### Hierarquia de Dados
```
Dominio
  └── Categoria (status=PENDING → APPROVED → REJECTED/AJUSTE)
        └── Subcategoria (status=PENDING → APPROVED → REJECTED/AJUSTE)
              └── Classificacao (termo ↔ subcategoria)
                    └── Termo (status=PENDING → APPROVED → REJECTED/AJUSTE)
                          └── Video (status=PENDING → APPROVED → REJECTED/AJUSTE)
```

### Relacionamentos (models.py - CORRETOS)
```python
class Categoria(models.Model):
    dominio = ForeignKey(Dominio)  # ✅
    
class Subcategoria(models.Model):
    categoria = ForeignKey(Categoria, related_name='subcategorias')  # ✅
    
class Classificacao(models.Model):
    termo = ForeignKey(Termo, related_name='classificacoes')  # ✅
    subcategoria = ForeignKey(Subcategoria, related_name='classificacoes')  # ✅
    
class Termo(models.Model):
    # Sem ForeignKey direto para Categoria ou Subcategoria
    # Acesso via: termo.classificacoes.all() → classificacao.subcategoria.categoria
    
class Video(models.Model):
    termo = ForeignKey(Termo, related_name='videos')  # ✅
```

---

## 🐛 BUGS ENCONTRADOS

### BUG #1: moderation_action() Não Aprova Categoria/Subcategoria
**Arquivo**: `apps/catalog/views.py`, linhas 339-371

**Código atual**:
```python
@login_required
def moderation_action(request, object_type, object_id, action):
    ...
    if object_type == 'termo':
        termo = get_object_or_404(Termo, id_termo=object_id)
        termo.status = novo_status
        termo.feedback = feedback
        termo.save(update_fields=['status', 'feedback'])
        
        # ✅ Aprova vídeos
        termo.videos.filter(
            status__in=['PENDING', 'AJUSTE']
        ).update(status=novo_status)
        
        # ❌ FALTA: Aprovar Categoria e Subcategoria!
        messages.success(...)
```

**Problema**: 
- Quando `novo_status = 'APPROVED'`, vídeos são aprovados mas Categoria/Subcategoria permanecem PENDING
- Resultado: Home não lista a categoria, navegação quebra

**Impacto**: 🔴 CRÍTICO

---

### BUG #2: moderation_action_categoria() Não Retorna Erro Explícito
**Arquivo**: `apps/catalog/views.py`, linhas 372-406

**Problema**: 
- Função parece correta, MAS pode retornar 400 se ação for inválida
- Sem logging suficiente para debugging

**Impacto**: 🟡 MENOR (já foi corrigido com action.strip().lower())

---

### BUG #3: Fluxo Manual vs Cascata
**Problema lógico**:
- Dashboard permite aprovar Categorias/Subcategorias **manualmente** E **via cascata**
- Quando aprova Termo → Subcategoria deveria ser auto-aprovada
- Quando aprova Termo → Categoria deveria ser auto-aprovada
- Mas usuário também pode clicar botão "Aprovar categoria" antes de aprovar Termo

**Cenários**:
1. ✅ Aprova Categoria → Subcategorias são auto-aprovadas (já implementado)
2. ❌ Aprova Termo → Categoria/Subcategoria NÃO são auto-aprovadas (BUG #1)
3. ✅ Aprova Subcategoria → funciona

**Impacto**: 🔴 CRÍTICO

---

## ✅ SOLUÇÃO

### Estratégia de Cascata (Bottom-Up)
Quando aprova um Termo:
1. ✅ Aprovar o Termo
2. ✅ Aprovar todos os Vídeos vinculados  
3. **→ Aprovar todas as Subcategorias relacionadas (via Classificacao)**
4. **→ Aprovar todas as Categorias relacionadas (via subcategoria.categoria)**

### Código da Solução

**Método novo em models.py - Termo:**
```python
def get_categorias(self):
    """Retorna todas as Categorias relacionadas via Classificacao."""
    return Categoria.objects.filter(
        subcategorias__classificacoes__termo=self
    ).distinct()

def get_subcategorias(self):
    """Retorna todas as Subcategorias relacionadas via Classificacao."""
    return Subcategoria.objects.filter(
        classificacoes__termo=self
    ).distinct()
```

**View modificada - moderation_action():**
```python
if object_type == 'termo':
    termo = get_object_or_404(Termo, id_termo=object_id)
    termo.status = novo_status
    termo.feedback = feedback
    termo.save(update_fields=['status', 'feedback'])

    # Aprova vídeos
    termo.videos.filter(
        status__in=['PENDING', 'AJUSTE']
    ).update(status=novo_status)
    
    # ✅ NOVO: Cascata de aprovação para Categoria/Subcategoria
    if novo_status == 'APPROVED':
        # Aprova todas as subcategorias relacionadas
        termo.get_subcategorias().filter(
            status__in=['PENDING', 'AJUSTE']
        ).update(status='APPROVED')
        
        # Aprova todas as categorias relacionadas
        termo.get_categorias().filter(
            status__in=['PENDING', 'AJUSTE']
        ).update(status='APPROVED')
```

---

## 📊 MATRIZ DE TESTESANÁLISE ATUALMENTE

### Cenário 1: Submissão Completa
1. Usuário submete: Categoria (NEW) + Subcategoria (NEW) + Termo (NEW) + Vídeo (NEW)
2. **Resultado BD**: Categoria=PENDING, Subcategoria=PENDING, Termo=PENDING, Vídeo=PENDING ✅
3. Moderador clica "Aprovar Termo"
4. **Esperado**: Categoria=APPROVED, Subcategoria=APPROVED, Termo=APPROVED, Vídeo=APPROVED
5. **Atual**: Categoria=PENDING ❌, Subcategoria=PENDING ❌, Termo=APPROVED ✅, Vídeo=APPROVED ✅

### Cenário 2: Rejeição em Cascata
1. Moderador clica "Rejeitar Termo"
2. **Esperado**: Termo=REJECTED, Vídeo=REJECTED, (Subcategoria e Categoria podem ficar PENDING ou rejeitar também)
3. **Atual**: Termo=REJECTED, Vídeo=REJECTED ✅

---

## 📝 ARQUIVOS IMPACTADOS

| Arquivo | Mudanças | Impacto |
|---------|----------|--------|
| `models.py` | Adicionar 2 métodos em Termo | Minor |
| `views.py` | Modificar `moderation_action()` | Critical |
| `urls.py` | Nenhuma | - |
| `template` | Nenhuma | - |

---

## 🚀 PRÓXIMAS ETAPAS

1. ✅ Adicionar métodos `get_categorias()` e `get_subcategorias()` em Termo
2. ✅ Modificar `moderation_action()` para cascata de aprovação
3. ✅ Testar cenários de aprovação/rejeição
4. ✅ Validar Home exibe categorias após aprovação

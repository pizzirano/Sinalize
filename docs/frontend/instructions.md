# Frontend Instructions — Sinalize

# Source of truth

Toda decisão visual deve seguir este documento.

Se houver conflito entre código e proposta visual:
este documento prevalece.

## Objetivo

Projeto voltado para acessibilidade digital para comunidade surda.

Regras:

## Regras estruturais do projeto

NÃO alterar:

apps/catalog/models.py
apps/catalog/apps.py
apps/forms/models.py
apps/forms/apps.py
apps/catalog/migrations/

NÃO mover apps internos.

Arquitetura oficial:

apps/
   catalog/
   forms/

config/settings/base.py:

sys.path.insert(
    0,
    str(BASE_DIR / "apps")
)

INSTALLED_APPS:

catalog
forms

- WCAG AAA
- Navegação teclado
- Dark-first
- Nunca usar cor como único indicador
- Compatível com daltonismo
- Priorizar leitura visual

---

# SIN-12 — Refatoração incremental

NUNCA alterar múltiplas páginas.

Ordem obrigatória:

SIN-12.1
Bootstrap

SIN-12.2
base.html

SIN-12.3
tokens

SIN-12.4
theme

SIN-12.5
focus + keyboard

Parar após cada etapa.

Validar Docker.

---

# Paleta oficial

bg-base:
#080f1a

bg-surface:
#0e1a2e

bg-card:
#112035

border:
#1a2f4a

accent-cyan:
#06d6c7

accent-amber:
#f59e0b

text-primary:
#e2e8f0

text-secondary:
#94a3b8

---

# Contraste

AAA >= 7:1

Nunca:

vermelho sozinho
verde sozinho

Sempre:

ícone
texto
cor

---

# UX Surdos

Espaçamento amplo

Hierarquia visual forte

Cards grandes

Player evidente

Textos curtos

Vídeos destacados

---

# Componentes futuros

SIN-14:

Home:
hero
carrossel
categorias

Termos:
sidebar

Sinais:
cards

Vídeos:
player

---

# Foco teclado

Adicionar:

focus-visible

outline:
3px ciano

Aplicar:

links
inputs
botões
cards

Adicionar:

skip link

---

# Não alterar ainda

HTMX
Busca
Uploads
Vídeos
Catálogo
SIN-13+
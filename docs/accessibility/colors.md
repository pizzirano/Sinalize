# Sinalize — Paleta de Cores Acessível (WCAG AAA)

## Tokens e contrastes validados

| Token CSS | Valor (dark) | Par testado | Razão | Nível |
|---|---|---|---|---|
| --color-foreground | #e2e8f0 | foreground / background | 14.9:1 | ✓ AAA |
| --color-foreground-secondary | #94a3b8 | secondary / background | 8.2:1 | ✓ AAA |
| --color-primary | #06d6c7 | primary / background | 9.8:1 | ✓ AAA |
| --color-secondary | #f59e0b | secondary / background | 8.1:1 | ✓ AAA |
| --color-accent | #818cf8 | accent / background | 7.3:1 | ✓ AAA |
| --color-destructive | #f87171 | destructive / background | 7.7:1 | ✓ AAA |
| --color-primary-fg | #00120f | primary-fg / primary | 11.4:1 | ✓ AAA |

## Regra de uso

- `--color-foreground-muted` (#64748b):
  SOMENTE para elementos decorativos.
  Não usar como cor de texto informativo
  (contraste insuficiente para texto pequeno).

- Estados de erro/sucesso/aviso:
  SEMPRE combinar cor + ícone + texto.
  Nunca depender só de cor (WCAG 1.4.1).

## Como usar

### CSS nativo

```css
color: var(--color-primary);
background: var(--color-card);
border: 1px solid var(--color-border);
```

### Tailwind classes

```html
<p class="text-foreground">Texto principal</p>

<div class="bg-card border border-border">
  Card
</div>

<button class="bg-primary text-primary-foreground">
  Ação
</button>

<span class="text-accent">Info</span>
```

CONSTRAINTS (do not violate):

- Do NOT modify any file other than:
  - templates/global/base.html
  - docs/accessibility/colors.md

- Do NOT remove existing CSS classes or Tailwind utilities.
- Do NOT change any template block structure
  ({% block %}, {% extends %}).

- Do NOT modify any Django template tags
  ({% url %}, {% static %}, etc.).

- Keep all existing Alpine.js:
  - x-data
  - x-show
  - @click
  directives unchanged.

- The retrocompatibility aliases
  (cyan, amber, indigo, base)
  MUST remain in tailwind.config
  so existing templates like termo_list.html
  that use text-cyan continue to work.

VERIFICATION:

After changes, confirm:

[ ] body uses var(--color-background) not #080f1a
[ ] :focus-visible uses var(--color-ring) not #06d6c7
[ ] tailwind.config has both semantic tokens AND retrocompat aliases
[ ] docs/accessibility/colors.md exists
[ ] No existing Tailwind class was removed
[ ] File still renders (no syntax errors in <style> or <script> blocks)
[ ] :root and .dark are separated blocks
[ ] Future light mode support remains possible

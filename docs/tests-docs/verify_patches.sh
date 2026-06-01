#!/usr/bin/bash
# SCRIPT DE VERIFICAÇÃO RÁPIDA
# Execute para verificar que todos os patches foram aplicados

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     VERIFICAÇÃO DE PATCHES - CASCATA DE APROVAÇÃO         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Verificar models.py
echo "[1] Verificando models.py..."
if grep -q "def get_subcategorias" apps/catalog/models.py; then
    echo "    ✅ Método get_subcategorias() encontrado"
else
    echo "    ❌ Método get_subcategorias() NÃO ENCONTRADO"
fi

if grep -q "def get_categorias" apps/catalog/models.py; then
    echo "    ✅ Método get_categorias() encontrado"
else
    echo "    ❌ Método get_categorias() NÃO ENCONTRADO"
fi

# 2. Verificar views.py
echo ""
echo "[2] Verificando views.py..."
if grep -q "termo.get_subcategorias()" apps/catalog/views.py; then
    echo "    ✅ Cascata de subcategorias implementada"
else
    echo "    ❌ Cascata de subcategorias NÃO ENCONTRADA"
fi

if grep -q "termo.get_categorias()" apps/catalog/views.py; then
    echo "    ✅ Cascata de categorias implementada"
else
    echo "    ❌ Cascata de categorias NÃO ENCONTRADA"
fi

if grep -q "Cascata: Termo" apps/catalog/views.py; then
    echo "    ✅ Logging de cascata implementado"
else
    echo "    ❌ Logging de cascata NÃO ENCONTRADO"
fi

# 3. Verificar documentação
echo ""
echo "[3] Verificando documentação..."
files=(\
    "DIAGNOSTICO_CASCATA.md"\
    "PATCHES_APLICADOS.md"\
    "RESUMO_EXECUTIVO.md"\
    "GUIA_PRATICO_TESTE.md"\
    "DEPLOYMENT_INSTRUCTIONS.md"\
    "ENTREGAVEIS_COMPLETOS.md"\
    "QUICK_START.md"\
    "validate_cascata.py"\
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "    ✅ $file"
    else
        echo "    ❌ $file - NÃO ENCONTRADO"
    fi
done

# 4. Resumo
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              VERIFICAÇÃO COMPLETA                         ║"
echo "║                                                            ║"
echo "║  Se todos os itens estão ✅, tudo foi aplicado            ║"
echo "║  Próximo passo: python validate_cascata.py               ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"

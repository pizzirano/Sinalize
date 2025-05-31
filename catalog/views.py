from django.shortcuts import render

def dominio_list(request):
    return render(request, 'catalog/pages/dominio.html', {
        'titulo': 'Lista de Domínios',
        'nivel': 'dominios',
        'dominio_id': 1  # Exemplo fixo
    })

def categoria_list(request, dominio_id):
    return render(request, 'catalog/pages/categorias.html', {
        'titulo': f'Categorias do Domínio {dominio_id}',
        'nivel': 'categorias',
        'dominio_id': dominio_id,
    })

def subcategoria_list(request, dominio_id, categoria_id):
    return render(request, 'catalog/pages/subcategorias.html', {
        'titulo': f'Subcategorias da Categoria {categoria_id}',
        'nivel': 'subcategorias',
        'dominio_id': dominio_id,
        'categoria_id': categoria_id,
    })

def termo_list(request, dominio_id, categoria_id, subcategoria_id):
    return render(request, 'catalog/pages/termos.html', {
        'titulo': f'Termos da Subcategoria {subcategoria_id}',
        'nivel': 'termos',
        'dominio_id': dominio_id,
        'categoria_id': categoria_id,
        'subcategoria_id': subcategoria_id,
    })

def termo_detail(request, dominio_id, categoria_id, subcategoria_id, termo_id):
    return render(request, 'catalog/pages/termo-view.html')
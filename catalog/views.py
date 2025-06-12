from django.shortcuts import render, get_object_or_404
from catalog.models import Termo, Categoria, Subcategoria, Video

def termo_list(request, categoria_id):
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    subcategorias = Subcategoria.objects.filter(categoria=categoria)

    context = {
        'categoria': categoria,
        'subcategorias': subcategorias,
    }

    return render(request, 'catalog/pages/termos.html', context)

def sinal_detail(request, dominio_id, categoria_id, subcategoria_id, termo_id):
    return render(request, 'catalog/pages/termo-view.html')

def home(request):
    termos_carrossel = Termo.objects.exclude(t_imagem='')
    categorias_galeria = Categoria.objects.filter(dominio_id=1)  # ou outro ID que desejar

    return render(request, 'catalog/pages/home.html', {
        'termos_carrossel': termos_carrossel,
        'categorias_galeria': categorias_galeria,
    })

def termos_por_subcategoria(request, subcategoria_id):
    subcategoria = get_object_or_404(Subcategoria, id_subcategoria=subcategoria_id)
    termos = Termo.objects.filter(classificacoes__subcategoria_id=subcategoria_id).distinct()

    return render(request, 'catalog/pages/termos.html', {
        'termos': termos,
        'subcategoria': subcategoria
    })

def sinal_list(request, termo_id):
    termo = get_object_or_404(Termo, id_termo=termo_id)
    videos = Video.objects.filter(termo_id=termo_id)

    context = {
        'termo': termo,
        'videos': videos,
    }

    return render(request, 'catalog/pages/sinal-list.html', context)
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from catalog.models import Termo, Categoria, Subcategoria, Video
from django.db.models import Count

# ------------------------------
# Lista termos de uma categoria
# ------------------------------
def termo_list(request, categoria_id):
    try:
        categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
        subcategorias = Subcategoria.objects.filter(categoria=categoria)

        # Filtro opcional por subcategoria (?sub=ID)
        sub_id = request.GET.get('sub')
        if sub_id:
            subcategoria = get_object_or_404(Subcategoria, id_subcategoria=sub_id, categoria=categoria)
            termos = Termo.objects.filter(
                classificacoes__subcategoria=subcategoria
            ).distinct()
        else:
            subcategoria = None
            termos = Termo.objects.filter(
                classificacoes__subcategoria__categoria=categoria
            ).distinct()

        context = {
            'categoria': categoria,
            'subcategorias': subcategorias,
            'termos': termos,
            'subcategoria': subcategoria,
        }
        return render(request, 'catalog/pages/termos.html', context)
    except Exception as e:
        return HttpResponse(f"Erro em termo_list: {e}", status=500)


def sinal_list(request, termo_id):
    """
    Lista todos os vídeos de um termo específico e exibe seus detalhes.
    """
    try:
        termo = get_object_or_404(Termo, id_termo=termo_id)
        videos = termo.videos.all()
        classificacoes = termo.classificacoes.select_related('subcategoria__categoria')

        context = {
            'termo': termo,
            'videos': videos,
            'classificacoes': classificacoes,
            'is_detail_page': True,
        }
        return render(request, 'catalog/pages/sinal-list.html', context)
    except Exception as e:
        return HttpResponse(f"Erro em sinal_list: {e}", status=500)
# ------------------------------
# Página inicial
# ------------------------------
def home(request):
    """
    Página inicial do sistema.
    Mostra termos para o carrossel e todas as categorias com imagem.
    """
    try:
        # Termos com imagem para o carrossel
        termos_carrossel = Termo.objects.filter(carrossel=True).exclude(t_imagem='')

        # Todas as categorias com imagem
        categorias_galeria = Categoria.objects.exclude(c_imagem='').filter(c_imagem__isnull=False)

        context = {
            'termos_carrossel': termos_carrossel,
            'categorias_galeria': categorias_galeria,
        }
        return render(request, 'catalog/pages/home.html', context)
    except Exception as e:
        return HttpResponse(f"Erro na home: {e}")
# ------------------------------
# Lista termos de uma subcategoria
# ------------------------------
def termos_por_subcategoria(request, subcategoria_id):
    """
    Exibe os termos pertencentes a uma subcategoria específica.
    Também envia a categoria associada (para o header e breadcrumb).
    """
    try:
        subcategoria = get_object_or_404(Subcategoria, id_subcategoria=subcategoria_id)
        categoria = subcategoria.categoria
        termos = Termo.objects.filter(classificacoes__subcategoria=subcategoria).distinct()
        subcategorias = Subcategoria.objects.filter(categoria=categoria)

        context = {
            'categoria': categoria,
            'subcategoria': subcategoria,
            'subcategorias': subcategorias,
            'termos': termos,
        }
        return render(request, 'catalog/pages/termos.html', context)
    except Exception as e:
        return HttpResponse(f"Erro em termos_por_subcategoria: {e}", status=500)


# ------------------------------
# Lista de vídeos (sinais) de um termo
# ------------------------------
def sinal_list(request, termo_id):
    """
    Lista todos os vídeos (sinais) associados a um termo.
    """
    try:
        termo = get_object_or_404(Termo, id_termo=termo_id)
        videos = Video.objects.filter(termo=termo)

        context = {
            'termo': termo,
            'videos': videos,
        }
        return render(request, 'catalog/pages/sinal-list.html', context)
    except Exception as e:
        return HttpResponse(f"Erro em sinal_list: {e}", status=500)


def video_detail(request, video_id):
    """
    Exibe o detalhe de um vídeo específico.
    """
    try:
        video = get_object_or_404(Video, id_video=video_id)
        termo = video.termo  # termo relacionado ao vídeo

        context = {
            'video': video,
            'termo': termo,
        }
        return render(request, 'catalog/pages/video-detail.html', context)
    except Exception as e:
        return HttpResponse(f"Erro em video_detail: {e}", status=500)
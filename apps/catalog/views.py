from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
import logging
from catalog.models import Termo, Categoria, Subcategoria, Video, Pertence, Classificacao

logger = logging.getLogger(__name__)

def can_view_submission(user, submission):
    if submission.status == 'APPROVED':
        return True
    if not user.is_authenticated:
        return False
    is_mod = user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['MODERATOR', 'ADMIN'])
    return is_mod or (submission.created_by == user)

def can_view_video(user, video):
    if video.status == 'APPROVED':
        return True
    if not user.is_authenticated:
        return False
    is_mod = user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['MODERATOR', 'ADMIN'])
    return is_mod or (video.uploaded_by == user)

def is_moderator(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['MODERATOR', 'ADMIN'])


# ------------------------------
# Lista termos de uma categoria
# ------------------------------
def termo_list(request, categoria_id):
    try:
        categoria = get_object_or_404(Categoria, id_categoria=categoria_id, status='APPROVED')
        subcategorias = Subcategoria.objects.filter(categoria=categoria, status='APPROVED')

        # Filtro opcional por subcategoria (?sub=ID)
        sub_id = request.GET.get('sub')
        if sub_id:
            subcategoria = get_object_or_404(Subcategoria, id_subcategoria=sub_id, categoria=categoria, status='APPROVED')
            termos = Termo.objects.filter(
                classificacoes__subcategoria=subcategoria,
                status='APPROVED'
            ).distinct()
        else:
            subcategoria = None
            termos = Termo.objects.filter(
                classificacoes__subcategoria__categoria=categoria,
                status='APPROVED'
            ).distinct()

        # Optional A–Z filter
        letra = request.GET.get('letra', '').strip().upper()
        if letra:
            try:
                accent_groups = {
                    'A': 'AÀÁÂÃÄÁÀÀÂÃ',
                    'B': 'B',
                    'C': 'CÇ',
                    'D': 'D',
                    'E': 'EÈÉÊË',
                    'F': 'F',
                    'G': 'G',
                    'H': 'H',
                    'I': 'IÌÍÎÏ',
                    'J': 'J',
                    'K': 'K',
                    'L': 'L',
                    'M': 'M',
                    'N': 'N',
                    'O': 'OÒÓÔÕÖ',
                    'P': 'P',
                    'Q': 'Q',
                    'R': 'R',
                    'S': 'S',
                    'T': 'T',
                    'U': 'UÙÚÛÜ',
                    'V': 'V',
                    'W': 'W',
                    'X': 'X',
                    'Y': 'Y',
                    'Z': 'Z',
                }
                chars = accent_groups.get(letra, letra)
                pattern = r'^[' + chars + r']'
                termos = termos.filter(nome_termo__iregex=pattern)
            except Exception as exc:
                logger.exception('Erro ao aplicar filtro por letra; fallback para istartswith')
                termos = termos.filter(nome_termo__istartswith=letra)

        context = {
            'categoria': categoria,
            'subcategorias': subcategorias,
            'termos': termos,
            'subcategoria': subcategoria,
            'letra': letra,
        }
        return render(request, 'catalog/pages/termos.html', context)
    except Exception as e:
        return HttpResponse(f"Erro em termo_list: {e}", status=500)


# ------------------------------
# Lista de vídeos (sinais) de um termo
# ------------------------------
def sinal_list(request, termo_id):
    try:
        termo = get_object_or_404(Termo, id_termo=termo_id)
        if not can_view_submission(request.user, termo):
            raise Http404("Termo não encontrado ou não está aprovado.")

        # Vídeos aprovados, ou se logado/mod, incluir pendentes do próprio autor
        if is_moderator(request.user):
            videos = termo.videos.all()
        elif request.user.is_authenticated:
            videos = termo.videos.filter(Q(status='APPROVED') | Q(uploaded_by=request.user))
        else:
            videos = termo.videos.filter(status='APPROVED')

        classificacoes = termo.classificacoes.select_related('subcategoria__categoria')

        context = {
            'termo': termo,
            'videos': videos,
            'classificacoes': classificacoes,
            'is_detail_page': True,
        }
        return render(request, 'catalog/pages/sinal-list.html', context)
    except Http404:
        raise
    except Exception as e:
        return HttpResponse(f"Erro em sinal_list: {e}", status=500)


# ------------------------------
# Detalhe do vídeo
# ------------------------------
def video_detail(request, video_id):
    try:
        video = get_object_or_404(Video, id_video=video_id)
        if not can_view_video(request.user, video):
            raise Http404("Vídeo não encontrado ou não está aprovado.")

        termo = video.termo
        context = {
            'video': video,
            'termo': termo,
        }
        return render(request, 'catalog/pages/video-detail.html', context)
    except Http404:
        raise
    except Exception as e:
        return HttpResponse(f"Erro em video_detail: {e}", status=500)


# ------------------------------
# Página inicial
# ------------------------------
def home(request):
    try:
        # Apenas termos APROVADOS no carrossel
        termos_carrossel = Termo.objects.filter(carrossel=True, status='APPROVED').exclude(t_imagem='')

        # Todas as categorias aprovadas com imagem
        categorias_galeria = Categoria.objects.filter(status='APPROVED').exclude(c_imagem='').filter(c_imagem__isnull=False)

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
    try:
        subcategoria = get_object_or_404(Subcategoria, id_subcategoria=subcategoria_id, status='APPROVED')
        categoria = subcategoria.categoria
        termos = Termo.objects.filter(classificacoes__subcategoria=subcategoria, status='APPROVED').distinct()
        subcategorias = Subcategoria.objects.filter(categoria=categoria, status='APPROVED')

        # Apply A–Z filter
        letra = request.GET.get('letra', '').strip().upper()
        if letra:
            try:
                accent_groups = {
                    'A': 'AÀÁÂÃÄÁÀÀÂÃ',
                    'B': 'B',
                    'C': 'CÇ',
                    'D': 'D',
                    'E': 'EÈÉÊË',
                    'F': 'F',
                    'G': 'G',
                    'H': 'H',
                    'I': 'IÌÍÎÏ',
                    'J': 'J',
                    'K': 'K',
                    'L': 'L',
                    'M': 'M',
                    'N': 'N',
                    'O': 'OÒÓÔÕÖ',
                    'P': 'P',
                    'Q': 'Q',
                    'R': 'R',
                    'S': 'S',
                    'T': 'T',
                    'U': 'UÙÚÛÜ',
                    'V': 'V',
                    'W': 'W',
                    'X': 'X',
                    'Y': 'Y',
                    'Z': 'Z',
                }
                chars = accent_groups.get(letra, letra)
                pattern = r'^[' + chars + r']'
                termos = termos.filter(nome_termo__iregex=pattern)
            except Exception:
                termos = termos.filter(nome_termo__istartswith=letra)

        context = {
            'categoria': categoria,
            'subcategoria': subcategoria,
            'subcategorias': subcategorias,
            'termos': termos,
            'letra': letra,
        }
        return render(request, 'catalog/pages/termos.html', context)
    except Exception as e:
        return HttpResponse(f"Erro em termos_por_subcategoria: {e}", status=500)


# ------------------------------
# Busca Viva (HTMX)
# ------------------------------
def live_search(request):
    query = request.GET.get('q', '').strip()
    termos = Termo.objects.none()
    if query:
        termos = Termo.objects.filter(status='APPROVED', nome_termo__icontains=query).distinct()

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'catalog/partials/search-results.html', {'termos': termos, 'query': query})

    return redirect('home')


# ------------------------------
# Painel de Moderação
# ------------------------------
@login_required
def moderation_dashboard(request):
    if not is_moderator(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Apenas moderadores podem acessar o painel administrativo.")

    termos_pendentes = Termo.objects.filter(status='PENDING').select_related('created_by').order_by('-created_at')
    videos_pendentes = Video.objects.filter(status='PENDING').select_related('uploaded_by', 'termo').order_by('id_video')
    categorias_pendentes = Categoria.objects.filter(status='PENDING').order_by('-id_categoria')
    subcategorias_pendentes = Subcategoria.objects.filter(status='PENDING').order_by('-id_subcategoria')

    return render(request, 'catalog/pages/moderation_dashboard.html', {
        'termos_pendentes': termos_pendentes,
        'videos_pendentes': videos_pendentes,
        'categorias_pendentes': categorias_pendentes,
        'subcategorias_pendentes': subcategorias_pendentes,
    })


@login_required
def moderation_action(request, object_type, object_id, action):
    if not is_moderator(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Apenas moderadores podem avaliar submissões.")

    if request.method == 'POST':
        feedback = request.POST.get('feedback', '').strip()
        action = action.strip().lower()

        MAP = {
            'aprovar':  'APPROVED',
            'rejeitar': 'REJECTED',
            'ajuste':   'AJUSTE',
        }

        if action not in MAP:
            return HttpResponseBadRequest()

        novo_status = MAP[action]

        if object_type == 'termo':
            termo = get_object_or_404(Termo, id_termo=object_id)

            # Atualiza o termo
            termo.status = novo_status
            termo.feedback = feedback
            termo.save(update_fields=['status', 'feedback'])

            # Propaga para todos os vídeos vinculados — aprovação em cascata
            termo.videos.filter(
                status__in=['PENDING', 'AJUSTE']
            ).update(status=novo_status)

            # ✅ NOVO: Cascata para Categoria e Subcategoria
            if novo_status == 'APPROVED':
                # Aprova todas as subcategorias relacionadas
                subcategorias = termo.get_subcategorias()
                subcategorias.filter(
                    status__in=['PENDING', 'AJUSTE']
                ).update(status='APPROVED')

                # Aprova todas as categorias relacionadas
                categorias = termo.get_categorias()
                categorias.filter(
                    status__in=['PENDING', 'AJUSTE']
                ).update(status='APPROVED')

                logger.info(
                    f"Cascata: Termo {termo.id_termo} aprovado. "
                    f"Subcategorias: {subcategorias.count()}, "
                    f"Categorias: {categorias.count()}"
                )

            messages.success(
                request,
                f'Termo "{termo.nome_termo}" e seus vídeos foram '
                f'{"aprovados" if novo_status == "APPROVED" else "atualizados"}.'
            )
        else:
            return HttpResponseBadRequest()

        if request.headers.get('HX-Request') == 'true':
            return HttpResponse("")

        return redirect('moderation_dashboard')

    return HttpResponse("Método de requisição inválido.", status=405)


@login_required
def moderation_action_categoria(request, category_id, action):
    if not is_moderator(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Apenas moderadores podem avaliar categorias.")

    if request.method != 'POST':
        return HttpResponse("Método de requisição inválido.", status=405)

    action = action.strip().lower()

    MAP = {
        'aprovar':  'APPROVED',
        'rejeitar': 'REJECTED',
        'ajuste':   'AJUSTE',
    }

    if action not in MAP:
        return HttpResponseBadRequest()

    categoria = get_object_or_404(Categoria, id_categoria=category_id)
    novo_status = MAP[action]
    categoria.status = novo_status
    categoria.save(update_fields=['status'])

    if action == 'aprovar':
        categoria.subcategorias.filter(status='PENDING').update(status='APPROVED')

    messages.success(request, f'Categoria "{categoria.nome_categoria}" atualizada com sucesso.')
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse("")
    return redirect('moderation_dashboard')


@login_required
def moderation_action_subcategoria(request, subcategory_id, action):
    if not is_moderator(request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Apenas moderadores podem avaliar subcategorias.")

    if request.method != 'POST':
        return HttpResponse("Método de requisição inválido.", status=405)

    action = action.strip().lower()

    MAP = {
        'aprovar':  'APPROVED',
        'rejeitar': 'REJECTED',
        'ajuste':   'AJUSTE',
    }

    if action not in MAP:
        return HttpResponseBadRequest()

    subcategoria = get_object_or_404(Subcategoria, id_subcategoria=subcategory_id)
    novo_status = MAP[action]
    subcategoria.status = novo_status
    subcategoria.save(update_fields=['status'])

    messages.success(request, f'Subcategoria "{subcategoria.nome_subcategoria}" atualizada com sucesso.')
    if request.headers.get('HX-Request') == 'true':
        return HttpResponse("")
    return redirect('moderation_dashboard')

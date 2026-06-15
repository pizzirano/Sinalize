from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse
from catalog.models import Termo, Video, Categoria, Subcategoria, Classificacao, Pertence, Dominio
from django.http import HttpResponse
from .forms import TermoForm, VideoForm, CategoriaForm, CustomAuthenticationForm, CustomUserCreationForm

@login_required
def cadastrar_termo_e_videos(request):
    VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=1, can_delete=False)

    if request.method == "POST":
        termo_form = TermoForm(request.POST, request.FILES)
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.none())

        if termo_form.is_valid() and formset.is_valid():
            dominio = termo_form.cleaned_data['dominio']
            categoria = termo_form.cleaned_data.get('categoria')
            nova_categoria = termo_form.cleaned_data.get('nova_categoria')
            imagem_categoria = termo_form.cleaned_data.get('imagem_categoria')
            subcategoria = termo_form.cleaned_data.get('subcategoria')
            nova_subcategoria = termo_form.cleaned_data.get('nova_subcategoria')

            if termo_form.cleaned_data.get('nao_encontrei_categoria'):
                categoria_obj = Categoria.objects.create(
                    nome_categoria=nova_categoria.strip(),
                    dominio=dominio,
                    c_imagem=imagem_categoria,
                    status='PENDING'
                )
            else:
                categoria_obj = categoria

            if nova_subcategoria:
                subcategoria_obj = Subcategoria.objects.create(
                    nome_subcategoria=nova_subcategoria.strip(),
                    categoria=categoria_obj,
                    status='PENDING'
                )
            else:
                subcategoria_obj = subcategoria

            termo = termo_form.save(commit=False)
            termo.created_by = request.user
            termo.status = 'PENDING'
            termo.save()

            Pertence.objects.get_or_create(termo=termo, dominio=dominio)
            if subcategoria_obj:
                Classificacao.objects.get_or_create(termo=termo, subcategoria=subcategoria_obj)

            for form in formset:
                if form.cleaned_data and form.cleaned_data.get('video'):
                    video = form.save(commit=False)
                    video.termo = termo
                    video.uploaded_by = request.user
                    video.status = 'PENDING'
                    video.convertido = False
                    video.save()

            messages.success(
                request,
                'Termo enviado com sucesso! Aguarde a análise do administrador.'
            )
            return redirect('forms:my_submissions')
    else:
        termo_form = TermoForm()
        formset = VideoFormSet(queryset=Video.objects.none())

    return render(request, 'forms/pages/signal_form.html', {
        'termo_form': termo_form,
        'formset': formset,
    })


@login_required
def my_submissions(request):
    termos = Termo.objects.filter(created_by=request.user).prefetch_related('videos').order_by('-created_at')
    return render(request, 'forms/pages/my_submissions.html', {
        'termos': termos,
    })


@login_required
def editar_termo(request, termo_id):
    termo = get_object_or_404(Termo, id_termo=termo_id, created_by=request.user)

    if termo.status not in ['PENDING', 'AJUSTE']:
        messages.error(request, "Você não pode editar um termo que já foi avaliado.")
        return redirect('forms:my_submissions')

    VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=0, can_delete=False)

    if request.method == "POST":
        termo_form = TermoForm(request.POST, request.FILES, instance=termo)
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.filter(termo=termo))

        if termo_form.is_valid() and formset.is_valid():
            dominio = termo_form.cleaned_data['dominio']
            categoria = termo_form.cleaned_data.get('categoria')
            nova_categoria = termo_form.cleaned_data.get('nova_categoria')
            imagem_categoria = termo_form.cleaned_data.get('imagem_categoria')
            subcategoria = termo_form.cleaned_data.get('subcategoria')
            nova_subcategoria = termo_form.cleaned_data.get('nova_subcategoria')

            if termo_form.cleaned_data.get('nao_encontrei_categoria'):
                categoria_obj = Categoria.objects.create(
                    nome_categoria=nova_categoria.strip(),
                    dominio=dominio,
                    c_imagem=imagem_categoria,
                    status='PENDING'
                )
            else:
                categoria_obj = categoria

            if nova_subcategoria:
                subcategoria_obj = Subcategoria.objects.create(
                    nome_subcategoria=nova_subcategoria.strip(),
                    categoria=categoria_obj,
                    status='PENDING'
                )
            else:
                subcategoria_obj = subcategoria

            termo = termo_form.save(commit=False)
            termo.status = 'PENDING'
            termo.feedback = None
            termo.save()

            Pertence.objects.get_or_create(termo=termo, dominio=dominio)
            if subcategoria_obj:
                Classificacao.objects.get_or_create(termo=termo, subcategoria=subcategoria_obj)

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    video = form.save(commit=False)
                    video.termo = termo
                    if not video.pk:
                        video.uploaded_by = request.user
                        video.convertido = False
                    video.status = 'PENDING'
                    if video.video:
                        video.save()

            messages.success(request, 'Sugestão atualizada! Aguarde nova análise.')
            return redirect('forms:my_submissions')
    else:
        initial_data = {}
        classificacao = termo.classificacoes.first()
        if classificacao:
            subcat = classificacao.subcategoria
            initial_data['subcategoria'] = subcat
            if subcat.categoria:
                initial_data['categoria'] = subcat.categoria
                initial_data['dominio'] = subcat.categoria.dominio

        termo_form = TermoForm(instance=termo, initial=initial_data)
        formset = VideoFormSet(queryset=Video.objects.filter(termo=termo))

    return render(request, 'forms/pages/signal_form.html', {
        'termo_form': termo_form,
        'formset': formset,
        'is_edit': True,
        'termo': termo,
    })


def subcategorias_por_categoria(request):
    categoria_id = request.GET.get('categoria')
    subs = Subcategoria.objects.filter(categoria_id=categoria_id, status='APPROVED') if categoria_id else Subcategoria.objects.none()
    return render(request, 'forms/partials/_subcategorias_options.html', {'subs': subs})


def login_view(request):
    """Custom login view with Tailwind-styled form"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_page = request.GET.get('next', 'catalog:home')
            return redirect(next_page)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def register(request):
    """Cadastro simples de usuário usando CustomUserCreationForm.

    Depois do registro o usuário é automaticamente autenticado e redirecionado para a home.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('catalog:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

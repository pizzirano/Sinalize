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
        categoria_form = CategoriaForm(request.POST, request.FILES)
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.none())

        if termo_form.is_valid() and formset.is_valid():
            nome_categoria = termo_form.cleaned_data['categoria'].strip()
            nome_subcategoria = termo_form.cleaned_data['subcategoria'].strip()

            dominio_turismo = Dominio.objects.get(pk=1)
            categoria_obj = Categoria.objects.filter(nome_categoria=nome_categoria, dominio=dominio_turismo).first()

            # Criar categoria se não existir e salvar a imagem
            if not categoria_obj:
                if categoria_form.is_valid() and categoria_form.cleaned_data.get('c_imagem'):
                    categoria_obj = Categoria.objects.create(
                        nome_categoria=nome_categoria,
                        dominio=dominio_turismo,
                        c_imagem=categoria_form.cleaned_data.get('c_imagem')
                    )
                else:
                    categoria_obj = Categoria.objects.create(
                        nome_categoria=nome_categoria,
                        dominio=dominio_turismo
                    )

            # Criar ou pegar subcategoria
            subcategoria_obj, _ = Subcategoria.objects.get_or_create(
                nome_subcategoria=nome_subcategoria,
                categoria=categoria_obj
            )

            # Salvar termo
            termo = termo_form.save(commit=False)
            termo.created_by = request.user
            termo.status = 'PENDING'
            termo.save()

            # Relacionamentos
            Pertence.objects.get_or_create(termo=termo, dominio=dominio_turismo)
            Classificacao.objects.get_or_create(termo=termo, subcategoria=subcategoria_obj)

            # Salvar vídeos
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

            # Always perform a normal redirect so Django messages are shown.
            return redirect('my_submissions')
    else:
        termo_form = TermoForm()
        categoria_form = CategoriaForm()
        formset = VideoFormSet(queryset=Video.objects.none())

    categorias_existentes = list(Categoria.objects.values_list('nome_categoria', flat=True).distinct())
    subcategorias_existentes = list(Subcategoria.objects.values_list('nome_subcategoria', flat=True).distinct())

    return render(request, 'forms/pages/signal_form.html', {
        'termo_form': termo_form,
        'categoria_form': categoria_form,
        'formset': formset,
        'categorias_existentes': categorias_existentes,
        'subcategorias_existentes': subcategorias_existentes,
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
        return redirect('my_submissions')

    VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=0, can_delete=False)

    if request.method == "POST":
        termo_form = TermoForm(request.POST, request.FILES, instance=termo)
        categoria_form = CategoriaForm(request.POST, request.FILES)
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.filter(termo=termo))

        if termo_form.is_valid() and formset.is_valid():
            nome_categoria = termo_form.cleaned_data['categoria'].strip()
            nome_subcategoria = termo_form.cleaned_data['subcategoria'].strip()

            dominio_turismo = Dominio.objects.get(pk=1)
            categoria_obj = Categoria.objects.filter(nome_categoria=nome_categoria, dominio=dominio_turismo).first()

            if not categoria_obj:
                if categoria_form.is_valid() and categoria_form.cleaned_data.get('c_imagem'):
                    categoria_obj = Categoria.objects.create(
                        nome_categoria=nome_categoria,
                        dominio=dominio_turismo,
                        c_imagem=categoria_form.cleaned_data.get('c_imagem')
                    )
                else:
                    categoria_obj = Categoria.objects.create(
                        nome_categoria=nome_categoria,
                        dominio=dominio_turismo
                    )

            subcategoria_obj, _ = Subcategoria.objects.get_or_create(
                nome_subcategoria=nome_subcategoria,
                categoria=categoria_obj
            )

            # Salvar termo
            termo = termo_form.save(commit=False)
            termo.status = 'PENDING'
            termo.feedback = None  # limpa feedback da moderação antiga
            termo.save()

            # Relacionamentos
            Pertence.objects.get_or_create(termo=termo, dominio=dominio_turismo)
            Classificacao.objects.get_or_create(termo=termo, subcategoria=subcategoria_obj)

            # Salvar vídeos e garantir status PENDING
            for form in formset:
                if form.cleaned_data and form.cleaned_data.get('video'):
                    video = form.save(commit=False)
                    video.termo = termo
                    video.status = 'PENDING'
                    video.save()

            messages.success(request, 'Sugestão atualizada! Aguarde nova análise.')
            return redirect('my_submissions')
    else:
        # Preenche com os dados de categoria e subcategoria do termo
        initial_data = {}
        classificacao = termo.classificacoes.first()
        if classificacao:
            subcat = classificacao.subcategoria
            initial_data['subcategoria'] = subcat.nome_subcategoria
            if subcat.categoria:
                initial_data['categoria'] = subcat.categoria.nome_categoria

        termo_form = TermoForm(instance=termo, initial=initial_data)
        categoria_form = CategoriaForm()
        formset = VideoFormSet(queryset=Video.objects.filter(termo=termo))

    categorias_existentes = list(Categoria.objects.values_list('nome_categoria', flat=True).distinct())
    subcategorias_existentes = list(Subcategoria.objects.values_list('nome_subcategoria', flat=True).distinct())

    return render(request, 'forms/pages/signal_form.html', {
        'termo_form': termo_form,
        'categoria_form': categoria_form,
        'formset': formset,
        'categorias_existentes': categorias_existentes,
        'subcategorias_existentes': subcategorias_existentes,
        'is_edit': True,
        'termo': termo,
    })


def login_view(request):
    """Custom login view with Tailwind-styled form"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_page = request.GET.get('next', 'home')
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
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

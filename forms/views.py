from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from catalog.models import Video, Categoria, Subcategoria, Classificacao, Pertence, Dominio
from .forms import TermoForm, VideoForm

def cadastrar_termo_e_videos(request):
    VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=1, can_delete=False)

    if request.method == "POST":
        termo_form = TermoForm(request.POST, request.FILES)
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.none())

        if termo_form.is_valid() and formset.is_valid():
            nome_categoria = termo_form.cleaned_data['categoria'].strip()
            nome_subcategoria = termo_form.cleaned_data['subcategoria'].strip()

            # Garante que domínio 1 (Turismo) exista
            dominio_turismo = Dominio.objects.get(pk=1)

            # Categoria: cria se não existir
            categoria_obj, _ = Categoria.objects.get_or_create(
                nome_categoria=nome_categoria,
                dominio=dominio_turismo
            )

            # Subcategoria: cria se não existir
            subcategoria_obj, _ = Subcategoria.objects.get_or_create(
                nome_subcategoria=nome_subcategoria,
                categoria=categoria_obj
            )

            # Salva o termo
            termo = termo_form.save(commit=False)
            termo.save()

            # Relaciona Pertence (domínio) e Classificação (subcategoria)
            Pertence.objects.get_or_create(termo=termo, dominio=dominio_turismo)
            Classificacao.objects.get_or_create(termo=termo, subcategoria=subcategoria_obj)

            # Salva vídeos
            for form in formset:
                if form.cleaned_data:
                    video = form.save(commit=False)
                    video.termo = termo
                    video.save()

            return redirect('home')
    else:
        termo_form = TermoForm()
        formset = VideoFormSet(queryset=Video.objects.none())

    # Listas para autocomplete
    categorias_existentes = Categoria.objects.values_list('nome_categoria', flat=True).distinct()
    subcategorias_existentes = Subcategoria.objects.values_list('nome_subcategoria', flat=True).distinct()

    return render(request, 'forms/pages/signal_form.html', {
        'termo_form': termo_form,
        'formset': formset,
        'categorias_existentes': categorias_existentes,
        'subcategorias_existentes': subcategorias_existentes,
    })
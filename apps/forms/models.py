from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from catalog.models import Video
from .forms import TermoForm, VideoForm

def cadastrar_termo_e_videos(request):
    VideoFormSet = modelformset_factory(Video, form=VideoForm, extra=2, can_delete=False)

    if request.method == "POST":
        termo_form = TermoForm(request.POST, request.FILES)
        formset = VideoFormSet(request.POST, request.FILES, queryset=Video.objects.none())

        if termo_form.is_valid() and formset.is_valid():
            termo = termo_form.save()
            for form in formset:
                if form.cleaned_data:  # só salva se o vídeo foi preenchido
                    video = form.save(commit=False)
                    video.termo = termo
                    video.save()
            return redirect('home')  # ajuste a URL de destino
    else:
        termo_form = TermoForm()
        formset = VideoFormSet(queryset=Video.objects.none())

    return render(request, 'forms/pages/signal_form.html', {
        'termo_form': termo_form,
        'formset': formset,
    })
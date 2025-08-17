from django import forms
from catalog.models import Termo, Video, Categoria, Subcategoria

class TermoForm(forms.ModelForm):
    categoria = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'list': 'categorias', 'class': 'form-control'})
    )
    subcategoria = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'list': 'subcategorias', 'class': 'form-control'})
    )

    class Meta:
        model = Termo
        fields = ['nome_termo', 'descricao', 't_imagem', 'carrossel', 'categoria', 'subcategoria']
        widgets = {
            'nome_termo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            't_imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'carrossel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['c_imagem']
        widgets = {
            'c_imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['titulo', 'tipo_video', 'video']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_video': forms.Select(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
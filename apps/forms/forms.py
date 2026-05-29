from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from catalog.models import Termo, Video, Categoria, Subcategoria

# Base Tailwind input class
TAILWIND_INPUT = 'mt-2 block w-full rounded-2xl border border-border bg-background px-4 py-3 text-foreground focus:border-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-ring'
TAILWIND_TEXTAREA = 'mt-2 block w-full rounded-2xl border border-border bg-background px-4 py-3 text-foreground focus:border-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-ring'
TAILWIND_SELECT = 'mt-2 block w-full rounded-2xl border border-border bg-background px-4 py-3 text-foreground focus:border-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-ring'
TAILWIND_CHECKBOX = 'w-4 h-4 rounded border-border'


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with Tailwind styling"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': TAILWIND_INPUT,
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
        })
    )


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with Tailwind styling"""
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
        })
    )
    password2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT,
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT}),
            'first_name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'last_name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
        }


class TermoForm(forms.ModelForm):
    categoria = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'list': 'categorias', 'class': TAILWIND_INPUT})
    )
    subcategoria = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'list': 'subcategorias', 'class': TAILWIND_INPUT})
    )

    class Meta:
        model = Termo
        fields = ['nome_termo', 'descricao', 't_imagem', 'carrossel', 'categoria', 'subcategoria']
        widgets = {
            'nome_termo': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': TAILWIND_TEXTAREA}),
            't_imagem': forms.ClearableFileInput(attrs={'class': 'mt-2 block w-full'}),
            'carrossel': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['c_imagem']
        widgets = {
            'c_imagem': forms.ClearableFileInput(attrs={'class': 'mt-2 block w-full'}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['titulo', 'tipo_video', 'video']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'tipo_video': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'video': forms.ClearableFileInput(attrs={'class': 'mt-2 block w-full'}),
        }
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from catalog.models import Termo, Video, Categoria, Subcategoria, Dominio

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
    nao_encontrei_categoria = forms.BooleanField(
        required=False,
        label='Não encontrei minha categoria'
    )
    dominio = forms.ModelChoiceField(
        queryset=Dominio.objects.none(),
        required=True,
        label='Domínio',
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.none(),
        required=False,
        label='Categoria existente',
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    subcategoria = forms.ModelChoiceField(
        queryset=Subcategoria.objects.none(),
        required=False,
        label='Subcategoria existente',
        widget=forms.Select(attrs={'class': TAILWIND_SELECT})
    )
    nova_categoria = forms.CharField(
        required=False,
        label='Nome da nova categoria',
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT})
    )
    imagem_categoria = forms.ImageField(
        required=False,
        label='Imagem da nova categoria',
        widget=forms.ClearableFileInput(attrs={'class': 'mt-2 block w-full'})
    )
    nova_subcategoria = forms.CharField(
        required=False,
        label='Nome da nova subcategoria',
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT})
    )

    class Meta:
        model = Termo
        fields = ['dominio', 'categoria', 'subcategoria', 'nova_categoria', 'imagem_categoria', 'nova_subcategoria', 'nome_termo', 'descricao', 't_imagem', 'carrossel']
        widgets = {
            'nome_termo': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': TAILWIND_TEXTAREA}),
            't_imagem': forms.ClearableFileInput(attrs={'class': 'mt-2 block w-full'}),
            'carrossel': forms.CheckboxInput(attrs={'class': TAILWIND_CHECKBOX}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['t_imagem'].required = False
        self.fields['categoria'].required = False
        self.fields['subcategoria'].required = False
        approved_categories = Categoria.objects.filter(status='APPROVED').order_by('nome_categoria')
        approved_subcategories = Subcategoria.objects.filter(status='APPROVED').order_by('nome_subcategoria')

        self.fields['dominio'].queryset = Dominio.objects.all().order_by('nome_dominio')
        self.fields['categoria'].queryset = approved_categories
        self.fields['subcategoria'].queryset = approved_subcategories

        base_class = ('mt-2 block w-full rounded-2xl border border-border '
                      'bg-background px-4 py-3 text-foreground '
                      'focus:border-primary focus:outline-none '
                      'focus-visible:ring-2 focus-visible:ring-ring')
        self.fields['categoria'].widget.attrs.update({
            'class': base_class,
            'hx-get': '/forms/subcategorias/',
            'hx-trigger': 'change',
            'hx-target': '#subcategoria_select',
            'hx-swap': 'innerHTML',
        })
        self.fields['subcategoria'].widget.attrs.update({
            'class': base_class,
            'id': 'subcategoria_select',
        })

        for field_name in ['nome_termo', 'descricao', 'nova_categoria', 'nova_subcategoria']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'class': base_class})

        if self.instance and self.instance.pk:
            classificacao = getattr(self.instance, 'classificacoes', None)
            if classificacao:
                classificacao = classificacao.first()
                if classificacao and classificacao.subcategoria:
                    current_subcategoria = classificacao.subcategoria
                    self.fields['subcategoria'].queryset = Subcategoria.objects.filter(
                        Q(status='APPROVED') | Q(pk=current_subcategoria.pk)
                    ).order_by('nome_subcategoria')
                    if current_subcategoria.categoria:
                        current_categoria = current_subcategoria.categoria
                        self.fields['categoria'].queryset = Categoria.objects.filter(
                            Q(status='APPROVED') | Q(pk=current_categoria.pk)
                        ).order_by('nome_categoria')

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        nao_encontrei_categoria = cleaned_data.get('nao_encontrei_categoria')
        nova_categoria = cleaned_data.get('nova_categoria')
        subcategoria = cleaned_data.get('subcategoria')
        nova_subcategoria = cleaned_data.get('nova_subcategoria')

        if nao_encontrei_categoria:
            cleaned_data['categoria'] = None
            if not nova_categoria:
                self.add_error(
                    'nova_categoria',
                    'Informe o nome da nova categoria.'
                )
        elif not categoria:
            self.add_error('categoria', 'Escolha uma categoria existente ou crie uma nova.')

        if nao_encontrei_categoria and not cleaned_data.get('imagem_categoria'):
            self.add_error(
                'imagem_categoria',
                'A imagem é obrigatória ao sugerir uma nova categoria.'
            )

        if not subcategoria and not nova_subcategoria:
            self.add_error('subcategoria', 'Escolha uma subcategoria existente ou crie uma nova.')

        return cleaned_data


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
        fields = ['titulo', 'tipo_video', 'descricao', 'video']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'tipo_video': forms.Select(attrs={'class': TAILWIND_SELECT}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': TAILWIND_TEXTAREA}),
            'video': forms.ClearableFileInput(attrs={'class': 'mt-2 block w-full'}),
        }

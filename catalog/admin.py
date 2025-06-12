from django.contrib import admin
from .models import (
    Dominio, Categoria, Subcategoria, Termo,
    Video, Classificacao, Pertence
)

# ---------- Inlines ----------

class ClassificacaoInline(admin.TabularInline):
    model = Classificacao
    extra = 1  # Número de linhas em branco para adicionar
    autocomplete_fields = ['subcategoria']  # Se quiser usar autocomplete

class PertenceInline(admin.TabularInline):
    model = Pertence
    extra = 1
    autocomplete_fields = ['dominio']

# ---------- Admin ----------

@admin.register(Dominio)
class DominioAdmin(admin.ModelAdmin):
    list_display = ('id_dominio', 'nome_dominio')
    search_fields = ('nome_dominio',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nome_categoria', 'dominio')
    search_fields = ('nome_categoria',)
    list_filter = ('dominio',)

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_subcategoria', 'nome_subcategoria', 'categoria')
    search_fields = ('nome_subcategoria',)
    list_filter = ('categoria',)

@admin.register(Termo)
class TermoAdmin(admin.ModelAdmin):
    list_display = ('id_termo', 'nome_termo', 'carrossel')
    search_fields = ('nome_termo',)
    list_filter = ('carrossel',)
    inlines = [ClassificacaoInline, PertenceInline]  # 👈 Aqui adiciona os dois

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id_video', 'titulo', 'tipo_video', 'termo')
    search_fields = ('titulo',)
    list_filter = ('tipo_video', 'termo')

# Não precisa mais registrar Classificacao e Pertence separadamente
# admin.site.register(Classificacao)
# admin.site.register(Pertence)
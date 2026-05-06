from django.db import models
import os
import subprocess
from django.conf import settings
from .utils import convert_video_to_mp4


class Dominio(models.Model):
    id_dominio = models.AutoField(primary_key=True)
    nome_dominio = models.CharField(max_length=30)

    def __str__(self):
        return self.nome_dominio


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=30)
    c_imagem = models.ImageField(upload_to='categorias/', null=True, blank=True)
    dominio = models.ForeignKey(Dominio, on_delete=models.CASCADE, related_name='categorias')

    def __str__(self):
        return self.nome_categoria


class Subcategoria(models.Model):
    id_subcategoria = models.AutoField(primary_key=True)
    nome_subcategoria = models.CharField(max_length=30)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias', null=True, blank=True)

    def __str__(self):
        return self.nome_subcategoria


class Termo(models.Model):
    id_termo = models.AutoField(primary_key=True)
    nome_termo = models.CharField(max_length=30)
    descricao = models.TextField(blank=True, null=True)
    t_imagem = models.ImageField(upload_to='termos/', null=True, blank=True)
    carrossel = models.BooleanField(default=False)

    def __str__(self):
        return self.nome_termo


class Video(models.Model):
    id_video = models.AutoField(primary_key=True)

    TIPOS_VIDEO = [
        ('Sinal', 'Sinal'),
        ('Soletrando', 'Termo em Libras Soletrando'),
        ('Significado', 'Significado'),
    ]

    tipo_video = models.CharField(max_length=20, choices=TIPOS_VIDEO)
    titulo = models.CharField(max_length=30)
    termo = models.ForeignKey('Termo', on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Salva o original

        if self.video and not self.video.name.lower().endswith('.mp4'):
            input_path = os.path.join(settings.MEDIA_ROOT, self.video.name)
            output_path = convert_video_to_mp4(input_path)

            if output_path:
                self.video.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
                super().save(update_fields=['video'])  # Salva com o novo caminho


class Classificacao(models.Model):
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE, related_name='classificacoes')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, related_name='classificacoes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['termo', 'subcategoria'], name='unique_classificacao')
        ]

    def __str__(self):
        return f"{self.termo} - {self.subcategoria}"


class Pertence(models.Model):
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE, related_name='pertencimentos')
    dominio = models.ForeignKey(Dominio, on_delete=models.CASCADE, related_name='pertencimentos')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['termo', 'dominio'], name='unique_pertence')
        ]

    def __str__(self):
        return f"{self.termo} pertence a {self.dominio}"
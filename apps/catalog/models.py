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
    STATUS_CHOICES = [
        ('PENDING',  'Pendente'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Rejeitado'),
        ('AJUSTE',   'Ajuste Solicitado'),
    ]

    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=30)
    c_imagem = models.ImageField(upload_to='categorias/', null=True, blank=True)
    dominio = models.ForeignKey(Dominio, on_delete=models.CASCADE, related_name='categorias')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='APPROVED',
        db_index=True
    )

    def __str__(self):
        return self.nome_categoria


class Subcategoria(models.Model):
    STATUS_CHOICES = [
        ('PENDING',  'Pendente'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Rejeitado'),
        ('AJUSTE',   'Ajuste Solicitado'),
    ]

    id_subcategoria = models.AutoField(primary_key=True)
    nome_subcategoria = models.CharField(max_length=30)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias', null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='APPROVED',
        db_index=True
    )

    def __str__(self):
        return self.nome_subcategoria


class Termo(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Rejeitado'),
        ('AJUSTE', 'Ajuste Solicitado'),
    ]

    id_termo = models.AutoField(primary_key=True)
    nome_termo = models.CharField(max_length=30)
    descricao = models.TextField(blank=True, null=True)
    t_imagem = models.ImageField(upload_to='termos/', null=True, blank=True)
    carrossel = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='termos_criados'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    @property
    def autor(self):
        return self.created_by

    def get_subcategorias(self):
        """
        Retorna todas as Subcategorias relacionadas via Classificacao.
        Usado para cascata de aprovação.
        """
        return Subcategoria.objects.filter(
            classificacoes__termo=self
        ).distinct()

    def get_categorias(self):
        """
        Retorna todas as Categorias relacionadas via Classificacao → Subcategoria.
        Usado para cascata de aprovação.
        """
        return Categoria.objects.filter(
            subcategorias__classificacoes__termo=self
        ).distinct()

    def __str__(self):
        return self.nome_termo


class Video(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('APPROVED', 'Aprovado'),
        ('REJECTED', 'Rejeitado'),
        ('AJUSTE', 'Ajuste Solicitado'),
    ]

    id_video = models.AutoField(primary_key=True)

    TIPOS_VIDEO = [
        ('Sinal', 'Sinal'),
        ('Datilologia', 'Datilologia'),
        ('Significado', 'Significado'),
    ]

    tipo_video = models.CharField(max_length=20, choices=TIPOS_VIDEO)
    titulo = models.CharField(max_length=30)
    termo = models.ForeignKey('Termo', on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='videos/')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='videos_enviados'
    )
    feedback = models.TextField(blank=True, null=True)
    convertido = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


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


class Profile(models.Model):
    ROLE_CHOICES = [
        ('COMMON', 'Usuário Comum'),
        ('MODERATOR', 'Moderador'),
        ('ADMIN', 'Administrador'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='COMMON'
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
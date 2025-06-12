from django.db import models

class Dominio(models.Model):
    id_dominio = models.AutoField(primary_key=True)
    nome_dominio = models.CharField(max_length=30)

    def __str__(self):
        return self.nome_dominio


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=30)
    c_imagem = models.ImageField(upload_to='categorias/', null=True, blank=True)  # NOVO
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
    t_imagem = models.ImageField(upload_to='termos/', null=True, blank=True)  # NOVO
    carrossel = models.BooleanField(default=False)  # NOVO

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
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.titulo


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
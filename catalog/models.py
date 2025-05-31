from django.db import models

class Dominio(models.Model):
    id_dominio = models.AutoField(primary_key=True)
    nome_dominio = models.CharField(max_length=30)

    def _str_(self):
        return self.nome_dominio


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=30)
    dominio = models.ForeignKey(Dominio, on_delete=models.CASCADE, related_name='categorias')

    def _str_(self):
        return self.nome_categoria


class Subcategoria(models.Model):
    id_subcategoria = models.AutoField(primary_key=True)
    nome_subcategoria = models.CharField(max_length=30)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias', null=True, blank=True)

    def _str_(self):
        return self.nome_subcategoria


class Termo(models.Model):
    id_termo = models.AutoField(primary_key=True)
    nome_termo = models.CharField(max_length=30)
    descricao = models.TextField(blank=True, null=True)

    def _str_(self):
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
    url = models.CharField(max_length=250, blank=True, null=True)
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='videos/')

    def _str_(self):
        return self.titulo


class Classificacao(models.Model):
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE, related_name='classificacoes')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, related_name='classificacoes')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['termo', 'subcategoria'], name='unique_classificacao')
        ]

    def _str_(self):
        return f"{self.termo} - {self.subcategoria}"


class Pertence(models.Model):
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE, related_name='pertencimentos')
    dominio = models.ForeignKey(Dominio, on_delete=models.CASCADE, related_name='pertencimentos')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['termo', 'dominio'], name='unique_pertence')
        ]

    def _str_(self):
        return f"{self.termo} pertence a {self.dominio}"
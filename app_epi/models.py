from django.db import models

# Create your models here.

class Epi(models.Model):
    nome = models.CharField(max_length=100)
    codigo_interno = models.CharField(max_length=20, blank=True, null=True)
    ca = models.CharField(max_length=20, unique=True, blank=True, null=True)
    tamanho = models.CharField(max_length=20, blank=True, null=True)
    vida_util_meses = models.PositiveIntegerField(blank=True, null=True)
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome


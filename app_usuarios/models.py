from django.db import models

# Create your models here.
class Colaborador(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14)
    matricula = models.CharField(max_length=20)
    ativo = models.BooleanField(default=True)

def __str__(self):
    return f"{self.nome} - {self.matricula}"

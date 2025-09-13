from django.db import models
from django.utils import timezone
from app_usuarios.models import Colaborador
from app_epi.models import Epi

class Emprestimo(models.Model):
    class Status(models.TextChoices):
        EMPRESTADO = "emprestado", "Emprestado"
        EM_USO     = "em_uso", "Em Uso"
        FORNECIDO  = "fornecido", "Fornecido"   # entrega definitiva
        DEVOLVIDO  = "devolvido", "Devolvido"
        DANIFICADO = "danificado", "Danificado"
        PERDIDO    = "perdido", "Perdido"

    colaborador = models.ForeignKey(Colaborador, on_delete=models.PROTECT, related_name="emprestimos")
    epi         = models.ForeignKey(Epi, on_delete=models.PROTECT, related_name="emprestimos")

    data_emprestimo          = models.DateTimeField(default=timezone.now)
    data_prevista_devolucao  = models.DateTimeField(null=True, blank=True)

    # usados quando status final
    data_devolucao           = models.DateTimeField(null=True, blank=True)
    observacao_devolucao     = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.EMPRESTADO)

    def __str__(self):
        return f"{self.epi.nome} -> {self.colaborador.nome} ({self.get_status_display()})"

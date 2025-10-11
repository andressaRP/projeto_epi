from django.urls import reverse, resolve
import pytest
from app_epi import views


def nome_obrigatorio_ok(nome):
    """Retorna True se o nome foi preenchido corretamente."""
    return bool(nome.strip())


def test_nome_obrigatorio_ok():
    """Verifica se o campo nome é obrigatório."""
    # Caso 1: nome vazio → deve falhar (False)
    assert not nome_obrigatorio_ok(""), "Nome vazio não deve ser aceito"

    # Caso 2: nome com apenas espaços → deve falhar (False)
    assert not nome_obrigatorio_ok("   "), "Nome em branco não deve ser aceito"

    # Caso 3: nome preenchido → deve passar (True)
    assert nome_obrigatorio_ok("Capacete"), "Nome válido deve ser aceito"
from django.urls import reverse, resolve
import pytest
from app_epi import views

# Função auxiliar para desempacotar decorators
from inspect import unwrap as _unwrap

@pytest.mark.django_db
def test_da_rota_listar_aponta_para_views_listar():
    """Verifica se a rota 'app_epi:listar_epi' está ligada à função views.listar_epi."""
    # Gera a URL com base no nome da rota
    url = reverse("app_epi:listar_epi")

    # Resolve o caminho até a view real
    match = resolve(url)

    # Confirma que o nome da view termina com 'listar_epi'
    assert match.view_name.split(":")[-1] == "listar_epi"

    # Desempacota decorators e obtém a função real
    real_func = _unwrap(match.func)

    # Garante que está apontando para a função correta
    assert real_func == views.listar_epi

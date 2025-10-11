import pytest
from django.urls import reverse, resolve
from app_usuarios import views

def _unwrap(func):
    # remove wrappers (login_required etc.) até chegar na função original
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func

def test_resolucao_da_rota_index_aponta_para_views_index():
    url = reverse("app_usuarios:index")     # nome da rota
    match = resolve(url)

    assert match.view_name.split(":")[-1] == "index"

    real_func = _unwrap(match.func)
    assert real_func == views.index


def rota_deletar_colaborador(colab_id: int) -> str:
    """Monta a URL da tela de confirmação de delete para um colaborador."""
    return reverse("app_usuarios:delete", kwargs={"id": colab_id})

def test_rota_deletar_colaborador():
    url = reverse("app_usuarios:delete", kwargs={"id": 42})
    assert url.endswith("/42/") 
from django.urls import reverse, resolve
from app_emprestimos import views

def _unwrap(func):
    # remove wrappers (ex.: login_required) para comparar com a função original
    while hasattr(func, "__wrapped__"):
        func = func.__wrapped__
    return func

def test_rota_relatorio_resolve_para_views_relatorio():
    url = reverse("app_emprestimos:relatorio")
    match = resolve(url)

    assert match.view_name.split(":")[-1] == "relatorio"

    assert _unwrap(match.func) == views.relatorio



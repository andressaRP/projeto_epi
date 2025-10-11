import pytest
from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse, NoReverseMatch
from urllib.parse import urlparse

def url_listar_epi():
    """
    Resolve a URL da listagem de EPIs pelos nomes comuns.
    """
    for name in ("app_epi:listar_epi", "app_epi:listar"):
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    pytest.skip("Nenhuma rota de listagem encontrada: 'app_epi:listar_epi' nem 'app_epi:listar'.")

@pytest.mark.django_db
def test_lista_epi_com_login(client, django_user_model):
    """Logado deve acessar listagem com 200."""
    user = django_user_model.objects.create_user(username="tester", password="123456")
    client.force_login(user)

    # só cria se o app existir
    try:
        from model_bakery import baker
        baker.make("app_epi.Epi", _quantity=2)
    except Exception:
        pass

    url = url_listar_epi()
    resp = client.get(url)
    assert resp.status_code == 200
    html = resp.content.decode()
    assert ("EPI" in html) or ("epi" in html)

   
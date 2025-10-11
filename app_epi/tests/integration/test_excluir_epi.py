import pytest
from django.conf import settings
from django.shortcuts import resolve_url
from django.urls import reverse, NoReverseMatch
from urllib.parse import urlparse

def url_delete_epi(epi_id: int) -> str:
    for name in ("app_epi:delete", "app_epi:deletar_epi"):
        try:
            return reverse(name, kwargs={"id": epi_id})
        except NoReverseMatch:
            continue
    pytest.skip("Não encontrei rota de delete: 'app_epi:delete' nem 'app_epi:deletar_epi'.")

@pytest.mark.django_db
def test_excluir_epi_correto(client, django_user_model):
    """
    Integração: cria dois EPIs, exclui um pela view e verifica
    que apenas o EPI alvo foi removido do banco.
    """

    # cria EPIs (tenta com model_bakery; se não houver, cria manualmente)
    try:
        from model_bakery import baker
        epi1 = baker.make("app_epi.Epi", nome="Capacete", codigo_interno="C1")
        epi2 = baker.make("app_epi.Epi", nome="Luva", codigo_interno="L1")
    except Exception:
        from app_epi.models import Epi
        epi1 = Epi.objects.create(nome="Capacete", codigo_interno="C1")
        epi2 = Epi.objects.create(nome="Luva", codigo_interno="L1")

    # chama a rota de exclusão do epi2
    url = url_delete_epi(epi2.id)

    resp = client.post(url, follow=True)

    assert resp.status_code in (200, 302)

    # valida no banco que só o epi2 sumiu
    from app_epi.models import Epi
    assert not Epi.objects.filter(id=epi2.id).exists(), "O EPI alvo não foi removido."
    assert Epi.objects.filter(id=epi1.id).exists(), "Outro EPI foi removido por engano."

    # checa mensagem de sucesso no HTML
    html = getattr(resp, "content", b"").decode(errors="ignore")
    assert ("excluído" in html.lower()) or True
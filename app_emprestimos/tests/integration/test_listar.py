import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_listar_emprestimos_quando_autenticado_responde_200(client, django_user_model):
    """Usuário logado acessa a lista e recebe 200."""
    user = django_user_model.objects.create_user(username="u1", password="123456")
    client.force_login(user)

    url = reverse("app_emprestimos:listar")
    resp = client.get(url)
    assert resp.status_code == 200    



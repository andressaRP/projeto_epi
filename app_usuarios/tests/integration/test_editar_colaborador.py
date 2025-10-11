import pytest
from django.urls import reverse
from app_usuarios.models import Colaborador


@pytest.mark.django_db
def test_editar_colaborador_salva_alteracoes(client, django_user_model):
    """Confirma se a edição de colaborador realmente salva as mudanças no banco."""
    # 1) Usuário logado
    user = django_user_model.objects.create_user(username="u1", password="123")
    client.force_login(user)

    # 2) Cria colaborador inicial
    colab = Colaborador.objects.create(
        nome="Ana Silva",
        cpf="000.000.000-00",
        matricula="A1"
    )

    # 3) Envia POST para editar
    url = reverse("app_usuarios:update", kwargs={"id": colab.id})
    novos_dados = {
        "nome": "Ana Souza",
        "cpf": "111.111.111-11",
        "matricula": "A2",
    }
    resp = client.post(url, novos_dados)

    # 4) Verifica se redirecionou (ou recarregou a página)
    assert resp.status_code in (200, 302)

    # 5) Atualiza o objeto no banco
    colab.refresh_from_db()

    # 6) Confirma que foi realmente alterado
    assert colab.nome == "Ana Souza"
    assert colab.cpf == "111.111.111-11"
    assert colab.matricula == "A2"
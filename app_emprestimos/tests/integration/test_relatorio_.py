import pytest
from django.urls import reverse
from django.utils import timezone

from app_usuarios.models import Colaborador
from app_epi.models import Epi
from app_emprestimos.models import Emprestimo

@pytest.fixture
def dados_base(db):
    """Cria alguns empréstimos para testar filtros por nome e EPI."""
    ana = Colaborador.objects.create(nome="Ana",  cpf="000.000.000-00", matricula="A1")
    beto = Colaborador.objects.create(nome="Beto", cpf="111.111.111-11", matricula="B2")

    capacete = Epi.objects.create(nome="Capacete", codigo_interno="EPI-001")
    luva     = Epi.objects.create(nome="Luva",     codigo_interno="EPI-002")

    now = timezone.now()
    # Ana - Capacete (EMPRESTADO)
    Emprestimo.objects.create(colaborador=ana,  epi=capacete,
                              status=Emprestimo.Status.EMPRESTADO,
                              data_emprestimo=now)
    # Beto - Luva (DEVOLVIDO)
    Emprestimo.objects.create(colaborador=beto, epi=luva,
                              status=Emprestimo.Status.DEVOLVIDO,
                              data_emprestimo=now)

    return {"ana": ana, "beto": beto, "capacete": capacete, "luva": luva, "now": now}

@pytest.mark.django_db
def test_relatorio_filtra_por_colaborador_nome(client, django_user_model, dados_base):
    user = django_user_model.objects.create_user(username="u1", password="123")
    client.force_login(user)

    url = reverse("app_emprestimos:relatorio")
    resp = client.get(url, {"colaborador_nome": "Ana"})
    assert resp.status_code == 200

    itens = list(resp.context["itens"])
    # Todos os itens devem ser da Ana
    assert itens, "Deveria retornar pelo menos 1 registro"
    assert all(e.colaborador.nome == "Ana" for e in itens), "Resultado deve conter apenas registros da Ana"

@pytest.mark.django_db
def test_relatorio_filtra_por_equipamento_nome(client, django_user_model, dados_base):
    user = django_user_model.objects.create_user(username="u1", password="123")
    client.force_login(user)

    url = reverse("app_emprestimos:relatorio")
    resp = client.get(url, {"equipamento_nome": "Capacete"})
    assert resp.status_code == 200

    itens = list(resp.context["itens"])
    # Todos os itens devem ser do EPI "Capacete"
    assert itens, "Deveria retornar pelo menos 1 registro"
    assert all(e.epi.nome == "Capacete" for e in itens), "Resultado deve conter apenas registros com EPI 'Capacete'"

@pytest.mark.django_db
def test_relatorio_filtra_por_status(client, django_user_model, dados_base):
    user = django_user_model.objects.create_user(username="u1", password="123")
    client.force_login(user)

    url = reverse("app_emprestimos:relatorio")
    resp = client.get(url, {"status": Emprestimo.Status.EMPRESTADO})
    assert resp.status_code == 200

    itens = list(resp.context["itens"])
    # Todos os itens devem estar EMPRESTADOS
    assert itens, "Deveria retornar pelo menos 1 registro"
    assert all(e.status == Emprestimo.Status.EMPRESTADO for e in itens), "Resultado deve conter apenas status EMPRESTADO"

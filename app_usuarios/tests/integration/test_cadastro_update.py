import pytest
from urllib.parse import urlsplit, parse_qs
from django.shortcuts import resolve_url
from django.urls import reverse

from app_usuarios.models import Colaborador

@pytest.mark.django_db
def test_cadastrar_colaborador_faltando_campos_obrigatorios(client):
    url = reverse("app_usuarios:cadastrar_colaborador")
    before = Colaborador.objects.count()

    # faltando campos obrigatórios -> view deve voltar 200 sem criar nada
    resp = client.post(url, data={"nome": ""})
    after = Colaborador.objects.count()

    assert resp.status_code == 200
    assert after == before


@pytest.mark.django_db
def test_cadastrar_colaborador_duplicado_mantem_um_registro(client):
    # já existe
    Colaborador.objects.create(nome="João", cpf="99988877766", matricula="M001")

    url = reverse("app_usuarios:cadastrar_colaborador")
    # tenta duplicar
    resp = client.post(url, data={"nome": "Maria", "cpf": "99988877766", "matricula": "M001"})
    assert resp.status_code == 200  # sem redirect de sucesso

    # continua só 1 registro para cada chave
    assert Colaborador.objects.filter(cpf="99988877766").count() == 1
    assert Colaborador.objects.filter(matricula="M001").count() == 1



@pytest.mark.django_db
def test_update_colaborador_nao_permite_cpf_duplicado(client, django_user_model):
    """
    Ao tentar editar um colaborador para usar um CPF já existente,
    a view deve responder 200 (erro de validação) e não alterar o registro.
    """
    # autentica (rotas protegidas)
    user = django_user_model.objects.create_user(username="tester", password="123456")
    client.force_login(user)

    # Dados iniciais
    a = Colaborador.objects.create(nome="Ana",  cpf="11122233344", matricula="A123")
    b = Colaborador.objects.create(nome="Bruno", cpf="55566677788", matricula="B456")

    url = reverse("app_usuarios:update", kwargs={"id": b.id})

    # Tenta editar o colaborador B para ter o CPF da Ana (duplicado)
    resp = client.post(url, data={
        "nome": "Bruno Editado",
        "cpf":  "11122233344",   # já existe no colaborador A
        "matricula": "B456",
    })

    # Em validação falha, a view renderiza a mesma página => 200 (sem redirect)
    assert resp.status_code == 200

    # Recarrega B do banco e verifica que NÃO mudou o CPF/nome
    b.refresh_from_db()
    assert b.cpf == "55566677788"
    assert b.nome == "Bruno"

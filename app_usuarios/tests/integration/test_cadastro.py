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
    assert resp.status_code == 200 
    assert "Já existe um colaborador com este CPF" in resp.content.decode() # sem redirect de sucesso

    # continua só 1 registro para cada chave
    assert Colaborador.objects.filter(cpf="99988877766").count() == 1
    assert Colaborador.objects.filter(matricula="M001").count() == 1


import pytest
from datetime import timedelta
from django.utils import timezone
from app_usuarios.models import Colaborador
from app_epi.models import Epi
from app_emprestimos.models import Emprestimo
from django.test import Client
from django.urls import reverse, resolve
from app_emprestimos import views
import app_emprestimos.views as emprestimos_views


@pytest.mark.django_db
def test_cadastrar_emprestado_sem_data_prevista_nao_cria_emprestimo(client, django_user_model, monkeypatch):
   
       # dados mínimos
    col = Colaborador.objects.create(nome="Ana", cpf="11122233344", matricula="A123")
    epi = Epi.objects.create(nome="Capacete", codigo_interno="E001")

    # controla as datas retornadas pela view (emp = agora, prevista = None)
    base = timezone.now()

    def fake_parse_dt(valor):
        if valor == "EMP":   # vamos mandar "EMP" no POST
            return base
        if valor == "PREV":  # vamos mandar "PREV" no POST (mas aqui queremos None)
            return None
        return None

    monkeypatch.setattr(emprestimos_views, "_parse_dt", fake_parse_dt)

    url = reverse("app_emprestimos:cadastrar")
    before = Emprestimo.objects.count()

    resp = client.post(url, data={
        "colaborador": col.id,
        "epi": epi.id,
        "status": Emprestimo.Status.EMPRESTADO,
        "data_emprestimo": "EMP",
        "data_prevista_devolucao": "PREV",  # fake_parse_dt -> None
        "condicao_emprestimo": "ok",
    })

    after = Emprestimo.objects.count()
    assert resp.status_code == 200      # volta ao formulário com erro
    assert after == before              # nada criado

@pytest.mark.django_db
def test_mostra_apenas_status_emprestado_e_fornecido_no_cadastramento(client, django_user_model):
    # autentica (rotas protegidas)
    user = django_user_model.objects.create_user(username="u1", password="123456")
    client.force_login(user)

    url = reverse("app_emprestimos:cadastrar")
    resp = client.get(url)
    assert resp.status_code == 200

    html = resp.content.decode().lower()

    # Deve conter essas duas opções
    assert 'value="emprestado"' in html or ">emprestado<" in html
    assert 'value="fornecido"' in html or ">fornecido<" in html

    # Não deve conter as demais
    assert 'value="devolvido"' not in html and ">devolvido<" not in html
    assert 'value="danificado"' not in html and ">danificado<" not in html
    assert 'value="perdido"' not in html and ">perdido<" not in html

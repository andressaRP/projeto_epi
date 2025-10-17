import uuid
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from app_usuarios.models import Colaborador
from app_epi.models import Epi
from app_emprestimos.models import Emprestimo

LOGIN_URL = "/login/"
FORM_URL  = "/emprestimos/novo/"   # ajuste se sua rota for outra

PAUSE = 0.5
def pause(t=PAUSE): time.sleep(t)

@pytest.mark.functional
def test_cadastrar_fornecimento_epi_bem_simples(live_server, browser, wait, django_user_model, db):
    # 1) usuário admin
    username, password = "admin", "admin123"
    user, _ = django_user_model.objects.get_or_create(
        username=username,
        defaults={"email": "a@a.com", "is_staff": True, "is_superuser": True},
    )
    user.set_password(password); user.save()

    # 2) dados mínimos: 1 colaborador + 1 EPI
    sufixo = uuid.uuid4().hex[:6].upper()
    colab = Colaborador.objects.create(
        nome=f"Ana Simples {sufixo}", cpf="000.000.000-00", matricula=f"A1{sufixo}"
    )
    epi = Epi.objects.create(nome=f"Capacete {sufixo}", codigo_interno=f"EPI-{sufixo}")

    # 3) login
    browser.get(live_server.url + LOGIN_URL); pause()
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username); pause()
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password); pause()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'],input[type='submit']"))).click()
    wait.until_not(EC.url_contains("login")); pause()

    # 4) abre formulário
    browser.get(live_server.url + FORM_URL); pause()

    # 5) seleciona colaborador, EPI e STATUS = fornecido (não exige data prevista)
    sel_colab  = wait.until(EC.presence_of_element_located((By.ID, "colaborador")))
    sel_epi    = wait.until(EC.presence_of_element_located((By.ID, "epi")))
    sel_status = wait.until(EC.presence_of_element_located((By.ID, "status"))); pause()

    Select(sel_colab).select_by_value(str(colab.id)); pause()
    Select(sel_epi).select_by_value(str(epi.id)); pause()
    Select(sel_status).select_by_value("fornecido"); pause()

    # 6) salva
    btn_salvar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']")))
    btn_salvar.click(); pause()

    # 7) valida no banco
    assert Emprestimo.objects.filter(
        colaborador=colab, epi=epi, status=Emprestimo.Status.FORNECIDO
    ).exists(), "Registro 'fornecido' não foi criado."

    # (opcional) confere algo na UI
    page = browser.find_element(By.TAG_NAME, "body").text
    assert (colab.nome in page) or (epi.nome in page) or ("sucesso" in page.lower())
    pause()

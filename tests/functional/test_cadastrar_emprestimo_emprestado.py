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
FORM_URL  = "/emprestimos/novo/" 

PAUSE = 0.5
def pause(t=PAUSE): time.sleep(t)

@pytest.mark.functional
def test_emprestar_epi_prevista_bem_futura(live_server, browser, wait, django_user_model, db):
    # --- usuário admin ---
    username, password = "admin", "admin123"
    user, _ = django_user_model.objects.get_or_create(
        username=username,
        defaults={"email": "a@a.com", "is_staff": True, "is_superuser": True},
    )
    user.set_password(password)
    user.save()

    # --- base: 1 colaborador + 1 EPI ---
    sufixo = uuid.uuid4().hex[:6].upper()
    colab = Colaborador.objects.create(
        nome=f"Ana Test {sufixo}", cpf="000.000.000-00", matricula=f"A1{sufixo}"
    )
    epi = Epi.objects.create(nome=f"Capacete {sufixo}", codigo_interno=f"EPI-{sufixo}")

    # --- login ---
    browser.get(live_server.url + LOGIN_URL); pause()
    wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username); pause()
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password); pause()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'],input[type='submit']"))).click()
    wait.until_not(EC.url_contains("login")); pause()

    # --- formulário de cadastro de empréstimo ---
    browser.get(live_server.url + FORM_URL); pause()

    sel_colab  = wait.until(EC.presence_of_element_located((By.ID, "colaborador")))
    sel_epi    = wait.until(EC.presence_of_element_located((By.ID, "epi")))
    sel_status = wait.until(EC.presence_of_element_located((By.ID, "status")))
   
    inp_prev   = wait.until(EC.presence_of_element_located((By.ID, "data_prevista_devolucao")))
    pause()

    # seleciona colaborador/EPI
    Select(sel_colab).select_by_value(str(colab.id)); pause()
    Select(sel_epi).select_by_value(str(epi.id)); pause()

    # status = emprestado (obriga prevista)
    Select(sel_status).select_by_value("emprestado"); pause()

    # define UMA DATA PREVISTA FUTURA (sem mexer no empréstimo)
    prevista_val = "2099-12-31T12:00"
    browser.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
        inp_prev, prevista_val
    )
    pause()

    # envia
    btn_salvar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']")))
    btn_salvar.click(); pause()

    # --- validação ---
    assert Emprestimo.objects.filter(
        colaborador=colab, epi=epi, status=Emprestimo.Status.EMPRESTADO
    ).exists(), "Empréstimo não foi criado no banco."

    body = browser.find_element(By.TAG_NAME, "body").text
    assert (colab.nome in body) or (epi.nome in body) or ("sucesso" in body.lower()), \
        "Não encontrei confirmação visível na UI (ajuste texto/rota pós-submit se necessário)."
    pause()

    

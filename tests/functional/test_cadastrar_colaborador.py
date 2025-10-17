import uuid
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

LOGIN_URL = "/login/"                               
FORM_URL  = "/usuarios/cadastrar_colaborador/"       

@pytest.mark.functional
def test_cadastrar_colaborador_com_login(live_server, browser, wait, django_user_model):
    # --- garante usuário admin ---
    username = "admin"
    password = "admin123"
    user, _ = django_user_model.objects.get_or_create(
        username=username,
        defaults={"email": "a@a.com", "is_staff": True, "is_superuser": True},
    )
    user.set_password(password)
    user.save()
    time.sleep(0.5)

    # --- faz login via UI ---
    browser.get(live_server.url + LOGIN_URL)

    # campos típicos do auth
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))).send_keys(username)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'],input[type='submit']"))).click()
    time.sleep(0.5)
    # confirma que NÃO estamos mais na tela de login (URL mudou / não contém "login")
    wait.until_not(EC.url_contains("login"))

    # --- abre o formulário protegido ---
    browser.get(live_server.url + FORM_URL)

    # captura inputs do seu template
    nome_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#nome[name='nome']")))
    cpf_el  = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#cpf[name='cpf']")))
    mat_el  = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#matricula[name='matricula']")))
    time.sleep(0.5)
    # --- dados únicos para evitar duplicidade ---
    sufixo = uuid.uuid4().hex[:5].upper()
    nome = f"Maria Silva {sufixo}"
    
    cpf  = f"123.456.{sufixo[:3]}-0{len(sufixo)%10}"
    matricula = f"M{uuid.uuid4().hex[:3].upper()}"

    # preenche
    nome_el.clear(); nome_el.send_keys(nome)
    cpf_el.clear();  cpf_el.send_keys(cpf)
    mat_el.clear();  mat_el.send_keys(matricula)

    # envia
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']"))).click()
    time.sleep(0.5)
    # --- valida pós-submit ---
    # 1ª tentativa: o próprio nome aparece (listagem/detalhe)
    try:
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), nome))
        return
    except TimeoutException:
        pass

    # 2ª tentativa: mensagem de sucesso
    try:
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "cadastrado com sucesso"))
        return
    except TimeoutException:
        pass

    # 3ª tentativa: tratativa de duplicidade (caso alguém rode o teste repetidamente sem isolar DB)
    page = browser.page_source.lower()
    if "já cadastrado" in page or "já existe" in page or "duplic" in page:
        pytest.skip("Cadastro não confirmado pois o sistema reportou duplicidade (nome/cpf/matrícula).")

    # se nada disso apareceu, falha com contexto
    raise AssertionError(
        "Não encontrei o nome cadastrado nem a mensagem de sucesso após o submit. "
        "Ajuste os textos esperados ou verifique para onde a view redireciona."
    )

   
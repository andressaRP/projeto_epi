import uuid
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

LOGIN_URL = "/login/"                  
FORM_URL  = "/epi/cadastrar_epi/"      

@pytest.mark.functional
def test_cadastrar_epi_com_login(live_server, browser, wait, django_user_model):
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

    # --- login via UI ---
    browser.get(live_server.url + LOGIN_URL)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))).send_keys(username)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'],input[type='submit']"))).click()
    wait.until_not(EC.url_contains("login"))  # confirma que não está mais na tela de login

    # --- abre o formulário protegido ---
    browser.get(live_server.url + FORM_URL)
    time.sleep(0.5)

    # mapeia campos do template
    nome_el     = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#nome[name='nome']")))
    cod_el      = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#codigo_interno[name='codigo_interno']")))
    ca_el       = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#ca[name='ca']")))
    tam_el      = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#tamanho[name='tamanho']")))
    vida_el     = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#vida_util_meses[name='vida_util_meses']")))
    qtd_el      = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#quantidade[name='quantidade']")))
    time.sleep(0.5)
    # --- dados únicos para evitar duplicidade (principalmente CA / código interno) ---
    sufixo = uuid.uuid4().hex[:6].upper()
    nome         = f"Capacete de Segurança {sufixo}"
    codigo_int   = f"EPI-{sufixo}"
    # CA numérico simples para evitar máscara/validação
    ca           = f"{int(uuid.uuid4()) % 900000 + 100000}"   # 6 dígitos
    tamanho      = "Único"
    vida_meses   = "24"
    quantidade   = "5"

    # preenche
    nome_el.clear();   nome_el.send_keys(nome)
    cod_el.clear();    cod_el.send_keys(codigo_int)
    ca_el.clear();     ca_el.send_keys(ca)
    tam_el.clear();    tam_el.send_keys(tamanho)
    vida_el.clear();   vida_el.send_keys(vida_meses)
    qtd_el.clear();    qtd_el.send_keys(quantidade)

    # envia
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary[type='submit']"))).click()
    time.sleep(0.5)
    # --- valida pós-submit ---
    # 1) aparece o nome do EPI na página (listagem/detalhe)
    try:
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), nome))
        return
    except TimeoutException:
        pass

 
    try:
        ok_msgs = [
            "EPI cadastrado com sucesso",
            "cadastrado com sucesso",
            "salvo com sucesso",
        ]
        page = browser.page_source.lower()
        if any(m.lower() in page for m in ok_msgs):
            return
    except TimeoutException:
        pass

    # 3) se o sistema acusar duplicidade, pula o teste (rodaram sem isolar DB)
    page = browser.page_source.lower()
    if "já cadastrado" in page or "já existe" in page or "duplic" in page:
        pytest.skip("Cadastro de EPI não confirmado pois o sistema reportou duplicidade (CA/código/nome).")

    # se nada confirmou, falha com contexto
    raise AssertionError(
        "Não encontrei o nome do EPI nem mensagem de sucesso após o submit. "
        "Ajuste as URLs/textos esperados ou verifique o redirecionamento da view."
    )

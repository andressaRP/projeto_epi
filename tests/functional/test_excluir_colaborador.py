import uuid
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from app_usuarios.models import Colaborador
from app_epi.models import Epi
from app_emprestimos.models import Emprestimo

LOGIN_URL = "/login/"
LIST_URL  = "/usuarios/index/"

@pytest.mark.functional
def test_listar_e_tentar_excluir_colaborador(live_server, browser, wait, django_user_model, db):
    # --- Garante usuário admin para login ---
    username, password = "admin", "admin123"
    user, _ = django_user_model.objects.get_or_create(
        username=username,
        defaults={"email": "a@a.com", "is_staff": True, "is_superuser": True},
    )
    user.set_password(password)
    user.save()

    # --- Cria dados de teste ---
    sufixo = uuid.uuid4().hex[:6].upper()

    colab_bloq = Colaborador.objects.create(
        nome=f"Ana Bloq {sufixo}", cpf="000.000.000-00", matricula=f"A1{sufixo}"
    )
    colab_livre = Colaborador.objects.create(
        nome=f"Beto Livre {sufixo}", cpf="111.111.111-11", matricula=f"B2{sufixo}"
    )

    epi = Epi.objects.create(nome=f"Capacete {sufixo}", codigo_interno=f"EPI-{sufixo}")
    Emprestimo.objects.create(colaborador=colab_bloq, epi=epi, status=Emprestimo.Status.EMPRESTADO)

    # --- Login via UI ---
    browser.get(live_server.url + LOGIN_URL)
    time.sleep(0.5)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))).send_keys(username)

    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))).send_keys(password)
   
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'],input[type='submit']"))).click()
    wait.until_not(EC.url_contains("login"))
    time.sleep(0.5)

    # --- Acessa lista ---
    browser.get(live_server.url + LIST_URL)
   

    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), colab_bloq.nome))
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), colab_livre.nome))
    time.sleep(0.5)

    # --- Função auxiliar: clicar "Deletar" na linha do nome desejado ---
    def clicar_deletar_do_nome(nome):
        linha = wait.until(EC.presence_of_element_located((
            By.XPATH,
            f"//table//tr[td[contains(normalize-space(.), '{nome}')]]"
        )))
        link_del = linha.find_element(By.XPATH, ".//a[contains(., 'Deletar')]")
       
        wait.until(EC.element_to_be_clickable(link_del)).click()
        time.sleep(0.5)

    # ========== 1) Tenta excluir colaborador BLOQUEADO ==========
    clicar_deletar_do_nome(colab_bloq.nome)

    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Excluir Colaborador"))
    time.sleep(0.5)

    body = browser.find_element(By.TAG_NAME, "body").text
    assert "Atenção" in body or "empréstimos vinculados" in body
    time.sleep(0.5)

    btn_excluir = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//button[contains(., 'Excluir')]")))
    btn_excluir.click()
    time.sleep(0.5)

    assert Colaborador.objects.filter(id=colab_bloq.id).exists(), "Colaborador com empréstimo não deveria ser excluído"
    time.sleep(0.5)

    browser.get(live_server.url + LIST_URL)
    time.sleep(0.5)
    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), colab_bloq.nome))
    time.sleep(0.5)

    # ========== 2) Exclui colaborador LIVRE ==========
    clicar_deletar_do_nome(colab_livre.nome)
    time.sleep(0.5)

    wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Excluir Colaborador"))
    time.sleep(0.5)

    btn_excluir = wait.until(EC.element_to_be_clickable((By.XPATH, "//form//button[contains(., 'Excluir')]")))
    btn_excluir.click()
    time.sleep(0.5)

    assert not Colaborador.objects.filter(id=colab_livre.id).exists(), "Colaborador livre deveria ter sido excluído"
    time.sleep(0.5)

    browser.get(live_server.url + LIST_URL)
    time.sleep(0.5)
    page = browser.find_element(By.TAG_NAME, "body").text
    assert colab_livre.nome not in page, "Nome do colaborador excluído ainda aparece na listagem"
    time.sleep(0.5)
    print("✅ Teste de exclusão de colaborador passou.")
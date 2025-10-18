import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.implicitly_wait(3)

try:
    driver.get("http://127.0.0.1:8000/")

    # espera o formulário de login
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username")))
    time.sleep(1)

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys("AndressaR")
    time.sleep(0.5)

    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys("leo123456")
    time.sleep(0.5)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # aguarda mudança de título OU mensagem de erro
    try:
        WebDriverWait(driver, 8).until(EC.title_contains("Sistema EPI"))
        titulo = driver.title
        if "Entrar" not in titulo:
            print("Login OK! Título:", titulo)
        else:
            raise TimeoutError("Ainda na tela de login.")
    except Exception:
        
        try:
            erro = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-danger"))
            )
            print("Login falhou. Mensagem exibida:", erro.text)
        except Exception:
            print("Login falhou, e não achei alerta. Título atual:", driver.title)

finally:
    time.sleep(2)  
    driver.quit()

print("Fim.")
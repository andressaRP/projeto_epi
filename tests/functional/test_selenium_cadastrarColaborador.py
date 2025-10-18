from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pytest

@pytest.mark.django_db
def test_cadastrar_colaborador():
  driver = webdriver.Chrome()
  driver.get("http://127.0.0.1:8000/login/")
  username_input = driver.find_element(By.NAME, "username")
  password_input = driver.find_element(By.NAME, "password")

  username_input.send_keys("AndressaR")
  password_input.send_keys("leo123456")

  submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
  submit_button.click()



  driver.get("http://127.0.0.1:8000/usuarios/cadastrar_colaborador/")
  nome_input = driver.find_element(By.NAME, "nome")
  cpf_input = driver.find_element(By.NAME, "cpf")
  matricula_input = driver.find_element(By.NAME, "matricula")
  submit_button = driver.find_element(By.XPATH, "/html/body/div[2]/main/div/form/div[4]/button")
  

  nome_input.send_keys("Ana Pereira")
  cpf_input.send_keys("093.805.219-52")
  matricula_input.send_keys("A12345")

  submit_button.click()  


  # Aguardar o alert aparecer
  wait = WebDriverWait(driver, 10)
  
  alert_message = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/main/div[1]/div"))).text

  assert "Colaborador cadastrado com sucesso!" in alert_message

  print("Resultado: Colaborador cadastrado com sucesso via Selenium.")


 
# Feche o navegador ao final
  driver.quit()   
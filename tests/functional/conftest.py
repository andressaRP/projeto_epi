import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="function")  # abre/fecha a cada teste — mais fácil de ver
def browser():
    opts = Options()
    # ⚠️ SEM HEADLESS:
    # NÃO adicione "--headless" aqui.
    opts.add_experimental_option("detach", True)  # mantém a janela aberta após o quit
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)

    try:
        yield driver
    finally:
        # dá um respiro pra você ver a janela antes de fechar
        time.sleep(2)
        driver.quit()

@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, 12)

@pytest.fixture
def f(browser, wait):
    class F:
        def by_id(self, el_id):
            return browser.find_element(By.ID, el_id)
        def must_see_text(self, text):
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text))
    return F()

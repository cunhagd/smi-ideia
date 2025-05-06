import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurações iniciais
DATA_DIR = os.path.join(os.getcwd(), "data")
CONFIG_DIR = os.path.join(os.getcwd(), "config")

# Função para configurar o driver do Selenium
def setup_driver():
    chrome_driver_path = os.path.join(CONFIG_DIR, "chromedriver.exe")
    service = Service(chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Maximiza a janela do navegador
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Função para carregar o arquivo noticias.json
def load_noticias_json(filename="noticias.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename="originals.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Função para extrair o link original de uma notícia
def extract_original_link(driver, url):
    driver.get(url)

    # Aguarda o carregamento do botão com o link original
    wait = WebDriverWait(driver, 20)
    try:
        # Localiza o botão pelo atributo onclick
        button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@onclick, 'window.open')]")))
        onclick_value = button.get_attribute("onclick")

        # Extrai o link original do atributo onclick
        start_index = onclick_value.find("'") + 1
        end_index = onclick_value.rfind("'")
        original_link = onclick_value[start_index:end_index]
        return original_link
    except Exception as e:
        print(f"Erro ao extrair o link original da notícia {url}: {e}")
        return None

# Função principal
def main():
    # Carrega os dados do arquivo noticias.json
    noticias_data = load_noticias_json()

    # Configura o driver do Selenium
    driver = setup_driver()

    # Lista para armazenar os dados atualizados
    updated_noticias_data = []

    try:
        for noticia in noticias_data:
            # Extrai o link original
            original_link = extract_original_link(driver, noticia["url"])

            # Atualiza os dados da notícia com o link original
            updated_noticia = {
                "url": noticia["url"],
                "url_original": original_link,
                "title": noticia["title"],
                "portal": noticia["portal"],
                "bloco": noticia["bloco"]
            }
            updated_noticias_data.append(updated_noticia)

        # Remove duplicatas com base no campo url_original
        unique_noticias_data = []
        seen_urls = set()  # Conjunto para rastrear URLs já processadas
        for noticia in updated_noticias_data:
            if noticia["url_original"] and noticia["url_original"] not in seen_urls:
                unique_noticias_data.append(noticia)
                seen_urls.add(noticia["url_original"])

        # Salva os dados atualizados no arquivo originals.json
        save_to_json(unique_noticias_data)
        print(f"{len(unique_noticias_data)} notícias foram salvas em {os.path.join(DATA_DIR, 'originals.json')}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
import os
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import sys


# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurações iniciais
DATA_DIR = os.path.join(os.getcwd(), "data")
CONFIG_DIR = os.path.join(os.getcwd(), "config")

# Função para configurar o driver do Selenium
def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Executar em modo headless (sem interface gráfica)
    options.add_argument("--no-sandbox")  # Necessário para ambientes como Railway
    options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória em contêineres
    service = Service("/app/config/chromedriver")  # Caminho para o chromedriver
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Função para carregar o arquivo duplicate.json
def load_duplicate_json(filename="duplicate.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename="scrap.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Função para extrair os dados de uma notícia
def extract_noticia_data(driver, url):
    driver.get(url)

    # Aguarda o carregamento da página
    wait = WebDriverWait(driver, 20)

    try:
        # Extrai o portal
        portal = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btNoVeiculo"))).text.strip()

        # Extrai o título
        titulo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dvTituloNoticia"))).text.strip()

        # Extrai o autor
        autor_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dvInfoNoticia > div > div:nth-child(3)")))
        autor_text = autor_element.text.strip()  # Exemplo: "Autor(a): Isabela Abalen"
        autor = autor_text.split(":", 1)[-1].strip()  # Remove o prefixo "Autor(a):"

        # Extrai o corpo da notícia
        corpo = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dvTextoNoticia > div.texto > article"))).text.strip()

        # Extrai a data e remove a hora
        data_completa = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dvTextoNoticia > div.info-veiculacao"))).text.strip()
        data = data_completa.split()[0]  # Mantém apenas a parte da data (DD/MM/AAAA)

        # Retorna os dados extraídos
        return {
            "portal": portal,
            "titulo": titulo,
            "autor": autor,
            "data": data,
            "corpo": corpo
        }
    except Exception as e:
        print(f"Erro ao extrair dados da notícia {url}: {e}")
        return None

# Função principal
def main():
    # Carrega os dados do arquivo duplicate.json
    noticias_data = load_duplicate_json()

    # Configura o driver do Selenium
    driver = setup_driver()

    # Lista para armazenar os dados das notícias processadas
    scrap_data = []

    try:
        for noticia in noticias_data:
            url = noticia["url"]
            url_original = noticia["url_original"]

            # Extrai os dados da notícia
            noticia_dados = extract_noticia_data(driver, url)

            if noticia_dados:
                # Atualiza os dados da notícia com os campos adicionais
                noticia_atualizada = {
                    "url": url,
                    "url_original": url_original,
                    **noticia_dados
                }
                scrap_data.append(noticia_atualizada)

        # Salva os dados atualizados no arquivo scrap.json
        save_to_json(scrap_data)
        print(f"{len(scrap_data)} notícias foram salvas em {os.path.join(DATA_DIR, 'scrap.json')}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
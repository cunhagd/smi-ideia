import os
import json
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações iniciais
BASE_URL = "https://c.ideiafixa.com.br/governodoestadomg/site/ideia/#"
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

# Função para extrair os links das notícias
def scrape_noticias(driver):
    driver.get(BASE_URL)

    # Aguarda o carregamento do menu
    wait = WebDriverWait(driver, 20)  # Aumenta o tempo de espera para 20 segundos

    # Verifica se há um iframe e alterna para ele, se necessário
    try:
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
    except:
        pass  # Se não houver iframe, continua normalmente

    # Passo 1: Clica no menu "Navegar"
    try:
        navegar_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Navegar']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", navegar_menu)
        ActionChains(driver).move_to_element(navegar_menu).click().perform()
    except Exception as e:
        print(f"Erro ao clicar no menu 'Navegar': {e}")
        driver.save_screenshot("debug_navegar.png")  # Tira um screenshot para depuração
        raise

    # Passo 2: Clica em "Sites e Blogs"
    try:
        sites_blogs_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Sites e Blogs']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", sites_blogs_menu)
        ActionChains(driver).move_to_element(sites_blogs_menu).click().perform()
    except Exception as e:
        print(f"Erro ao clicar no menu 'Sites e Blogs': {e}")
        driver.save_screenshot("debug_sites_blogs.png")  # Tira um screenshot para depuração
        raise

    # Aguarda o carregamento das notícias
    noticias = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.heading-title-link")))

    # Extrai os dados das notícias
    noticias_data = []
    for noticia in noticias:
        try:
            # Extrai o link da notícia
            href = noticia.get_attribute("href")
            full_url = urljoin(BASE_URL, href)  # Constrói a URL completa

            # Extrai o título da notícia
            titulo = noticia.text.strip()

            # Extrai o ID da notícia do link
            noticia_id = full_url.split("cd_noticia=")[-1]

            # Constrói o seletor dinâmico para o nome do portal
            portal_selector = f"#noticia_{noticia_id} > div.entry-meta > div > span > a > span:nth-child(1)"
            portal_element = driver.find_element(By.CSS_SELECTOR, portal_selector)
            portal = portal_element.text.strip()

            # Cria o dicionário com os dados da notícia
            noticia_info = {
                "url": full_url,
                "title": titulo,
                "portal": portal,
                "bloco": "Web"
            }
            noticias_data.append(noticia_info)
        except Exception as e:
            print(f"Erro ao processar uma notícia: {e}")
            continue

    return noticias_data

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename="noticias.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Função principal
def main():
    # Verifica se a pasta /data existe, caso contrário cria
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Configura o driver e realiza o scraping
    driver = setup_driver()
    try:
        noticias_data = scrape_noticias(driver)
        save_to_json(noticias_data)
        print(f"{len(noticias_data)} notícias foram salvas em {os.path.join(DATA_DIR, 'noticias.json')}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
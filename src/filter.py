import os
import json
import sys
# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.keywords import palavras_obrigatorias, palavras_adicionais

# Configurações iniciais
DATA_DIR = os.path.join(os.getcwd(), "data")

# Função para carregar o arquivo scrap.json
def load_scrap_json(filename="scrap.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename="filter.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Função para verificar se uma notícia é útil e extrair as palavras-chave encontradas
def is_noticia_util(titulo, corpo):
    # Combina o título e o corpo da notícia em um único texto
    texto_completo = f"{titulo} {corpo}".lower()

    # Encontra as palavras-chave obrigatórias presentes no texto
    obrigatorias_encontradas = [palavra for palavra in palavras_obrigatorias if palavra.lower() in texto_completo]

    # Encontra as palavras-chave adicionais presentes no texto
    adicionais_encontradas = [palavra for palavra in palavras_adicionais if palavra.lower() in texto_completo]

    # Verifica se a palavra "Zema" está presente no texto
    cita_gov = "zema" in texto_completo

    # A notícia é útil apenas se houver pelo menos 1 palavra obrigatória e 1 palavra adicional
    return obrigatorias_encontradas, adicionais_encontradas, cita_gov

# Função principal
def main():
    # Carrega os dados do arquivo scrap.json
    noticias_data = load_scrap_json()

    # Lista para armazenar as notícias úteis
    noticias_uteis = []

    for noticia in noticias_data:
        titulo = noticia.get("title", "").strip()
        corpo = noticia.get("corpo", "").strip()

        # Verifica se a notícia é útil e extrai as palavras-chave encontradas
        obrigatorias_encontradas, adicionais_encontradas, cita_gov = is_noticia_util(titulo, corpo)

        # Se a notícia for útil, adiciona à lista com os novos parâmetros
        if obrigatorias_encontradas and adicionais_encontradas:
            # Define o valor de 'relevancia' com base em 'cita_gov'
            relevancia = 'Útil' if cita_gov else None

            noticia_atualizada = {
                **noticia,
                "obrigatorias": ", ".join(obrigatorias_encontradas),
                "adicionais": ", ".join(adicionais_encontradas),
                "cita_gov": cita_gov,  # Adiciona o parâmetro 'cita_gov'
                "relevancia": relevancia  # Adiciona o novo parâmetro 'relevancia'
            }
            noticias_uteis.append(noticia_atualizada)

    # Salva as notícias úteis no arquivo filter.json
    save_to_json(noticias_uteis)
    print(f"{len(noticias_uteis)} notícias úteis foram salvas em {os.path.join(DATA_DIR, 'filter.json')}")

if __name__ == "__main__":
    main()
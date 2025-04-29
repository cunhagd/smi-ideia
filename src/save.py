import os
import json
import psycopg2
from config.dic import portais  # Importa o dicionário de portais

# Configurações iniciais
DATA_DIR = os.path.join(os.getcwd(), "data")
DB_URL = "postgresql://postgres:HomctJkRyZIGzYhrlmFRdKHZPJJmWylh@metro.proxy.rlwy.net:30848/railway"

# Função para carregar o arquivo scrap.json
def load_scrap_json(filename="scrap.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    # Carrega o conteúdo atual do arquivo, se ele existir
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Verifica se cada item já existe no arquivo com base no 'url_original'
    for item in data:
        if not any(existing_item.get("url_original") == item.get("url_original") for existing_item in existing_data):
            existing_data.append(item)

    # Salva o conteúdo atualizado no arquivo
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

# Função para conectar ao banco de dados PostgreSQL
def connect_to_db():
    try:
        connection = psycopg2.connect(DB_URL)
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return connection
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

# Função para verificar se um link já existe no banco de dados
def check_link_in_db(connection, link):
    try:
        cursor = connection.cursor()
        query = "SELECT EXISTS(SELECT 1 FROM noticias WHERE link = %s)"
        cursor.execute(query, (link,))
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists
    except Exception as e:
        print(f"Erro ao verificar o link no banco de dados: {e}")
        raise

def save_noticia(connection, noticia):
    try:
        cursor = connection.cursor()

        # Extrai os dados da notícia
        url_original = noticia.get("url_original", "").strip()
        url = noticia.get("url", "").strip()
        titulo = noticia.get("titulo", "").strip()
        data = noticia.get("data", "").strip()
        corpo = noticia.get("corpo", "").strip()
        autor = noticia.get("autor", "").strip()
        portal = noticia.get("portal", "").strip()
        obrigatorias = noticia.get("obrigatorias", "").strip()  # Garante que seja uma string
        adicionais = noticia.get("adicionais", "").strip()      # Garante que seja uma string
        cita_gov = noticia.get("cita_gov", False)
        relevancia = noticia.get("relevancia", None)

        # Logs para depuração
        print(f"Processando notícia: {url_original}")
        print(f"Obrigatorias: {obrigatorias}")
        print(f"Adicionais: {adicionais}")
        print(f"Relevancia: {relevancia}")

        # Verifica se o portal está no dicionário de portais
        if portal in portais:
            abrangencia = portais[portal].get("abrangencia", "Desconhecida")
            pontos = portais[portal].get("pontos", 0)  # Substitui valores inválidos por 0
            if pontos == "":
                pontos = 0
        else:
            # Se o portal não está no dicionário, salva a notícia no arquivo portais_erro.json
            save_to_json([noticia], "portais_erro.json")
            print(f"Portal '{portal}' não encontrado no dicionário. Notícia ignorada e salva em portais_erro.json.")
            return None

        # Define o valor True para a coluna 'ideiafixa'
        ideiafixa = True

        # Query para inserir os dados na tabela noticias
        query = """
        INSERT INTO noticias (
            link, link_ideia, titulo, data, corpo, autor, portal,
            obrigatorias, adicionais, cita_gov, relevancia,
            abrangencia, pontos, ideiafixa
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            url_original, url, titulo, data, corpo, autor, portal,
            obrigatorias, adicionais, cita_gov, relevancia,
            abrangencia, pontos, ideiafixa
        )

        cursor.execute(query, values)
        connection.commit()
        print(f"Notícia salva com sucesso: {url_original}")

        # Retorna os dados da notícia para serem salvos no save.json
        return {
            "url": url,
            "url_original": url_original,
            "titulo": titulo,
            "data": data,
            "corpo": corpo,
            "autor": autor,
            "portal": portal,
            "obrigatorias": obrigatorias,
            "adicionais": adicionais,
            "cita_gov": cita_gov,
            "relevancia": relevancia,
            "abrangencia": abrangencia,
            "pontos": pontos,
            "ideiafixa": ideiafixa
        }
    except Exception as e:
        print(f"Erro ao salvar a notícia {url_original}: {e}")
        connection.rollback()
        raise
    finally:
        cursor.close()

# Função principal
def main():
    # Carrega os dados do arquivo scrap.json
    noticias_data = load_scrap_json()

    # Conecta ao banco de dados
    connection = connect_to_db()

    # Lista para armazenar as notícias que foram salvas no banco de dados
    noticias_salvas = []

    try:
        for noticia in noticias_data:
            url_original = noticia.get("url_original", "").strip()

            # Verifica se o link já existe no banco de dados
            if not check_link_in_db(connection, url_original):
                # Salva a notícia no banco de dados e obtém os dados para o save.json
                noticia_salva = save_noticia(connection, noticia)
                if noticia_salva:
                    noticias_salvas.append(noticia_salva)
            else:
                print(f"Notícia já existe no banco de dados: {url_original}")

        # Salva as notícias salvas no arquivo save.json
        save_to_json(noticias_salvas, "save.json")
        print(f"{len(noticias_salvas)} notícias foram salvas em {os.path.join(DATA_DIR, 'save.json')}")

    finally:
        # Fecha a conexão com o banco de dados
        connection.close()

if __name__ == "__main__":
    main()
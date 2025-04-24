import os
import json
import psycopg2

# Configurações iniciais
DATA_DIR = os.path.join(os.getcwd(), "data")
DB_URL = "postgresql://postgres:HomctJkRyZIGzYhrlmFRdKHZPJJmWylh@metro.proxy.rlwy.net:30848/railway"

# Função para carregar o arquivo originals.json
def load_originals_json(filename="originals.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename="duplicate.json"):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

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

# Função principal
def main():
    # Carrega os dados do arquivo originals.json
    noticias_data = load_originals_json()

    # Conecta ao banco de dados
    connection = connect_to_db()

    # Lista para armazenar as notícias que não estão no banco de dados
    noticias_novas = []

    try:
        for noticia in noticias_data:
            url_original = noticia.get("url_original")

            if url_original:
                # Verifica se o link já existe no banco de dados
                if not check_link_in_db(connection, url_original):
                    # Se o link não existe, adiciona a notícia à lista de novas notícias
                    noticias_novas.append(noticia)
                else:
                    print(f"Link já existe no banco de dados: {url_original}")
            else:
                print("Notícia ignorada por não ter url_original.")

        # Salva as novas notícias no arquivo duplicate.json
        save_to_json(noticias_novas)
        print(f"{len(noticias_novas)} notícias foram salvas em {os.path.join(DATA_DIR, 'duplicate.json')}")

    finally:
        # Fecha a conexão com o banco de dados
        connection.close()

if __name__ == "__main__":
    main()
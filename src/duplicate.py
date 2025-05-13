import os
import json
import psycopg2
import sys
# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

# Função para verificar se um link já existe no banco de dados e em qual tabela
def check_link_in_db(connection, link):
    try:
        cursor = connection.cursor()
        tabelas = []
        
        # Verifica na tabela noticias
        query_noticias = "SELECT EXISTS(SELECT 1 FROM noticias WHERE link = %s)"
        cursor.execute(query_noticias, (link,))
        if cursor.fetchone()[0]:
            tabelas.append("noticias")
        
        # Verifica na tabela lixeira
        query_lixeira = "SELECT EXISTS(SELECT 1 FROM lixeira WHERE link = %s)"
        cursor.execute(query_lixeira, (link,))
        if cursor.fetchone()[0]:
            tabelas.append("lixeira")
        
        cursor.close()
        
        # Retorna a lista de tabelas onde o link foi encontrado (vazia se não encontrado)
        return tabelas
        
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
                # Verifica em quais tabelas o link já existe
                tabelas_com_link = check_link_in_db(connection, url_original)
                
                if not tabelas_com_link:
                    # Se o link não existe em nenhuma tabela, adiciona a notícia à lista de novas notícias
                    noticias_novas.append(noticia)
                else:
                    # Informa em quais tabelas o link foi encontrado
                    tabelas_str = ", ".join(tabelas_com_link)
                    print(f"Link já existe nas tabelas: {tabelas_str} - {url_original}")
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
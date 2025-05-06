import json
import psycopg2
from urllib.parse import urlparse
import os
import sys
# Adiciona o diretório raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Database connection URL
DB_URL = "postgresql://postgres:HomctJkRyZIGzYhrlmFRdKHZPJJmWylh@metro.proxy.rlwy.net:30848/railway"

def get_db_params(db_url):
    """Parse the database URL and return connection parameters."""
    parsed = urlparse(db_url)
    return {
        'dbname': parsed.path.lstrip('/'),
        'user': parsed.username,
        'password': parsed.password,
        'host': parsed.hostname,
        'port': parsed.port
    }

def clean_url(url):
    """Extract the main domain from a URL (e.g., 'https://www.em.com.br/path' -> 'em.com.br')."""
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def get_portal_name_from_db(url_original):
    """Query the portais table to find the portal name based on the cleaned URL."""
    cleaned_url = clean_url(url_original)
    try:
        conn = psycopg2.connect(**get_db_params(DB_URL))
        cur = conn.cursor()
        
        # Query all portals to compare cleaned URLs
        cur.execute("SELECT nome, url FROM portais")
        portals = cur.fetchall()
        
        for nome, portal_url in portals:
            if clean_url(portal_url) == cleaned_url:
                return nome
        
        return None  # Return None if no match is found
    
    except Exception as e:
        print(f"Error querying portais table: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def main():
    """Read filter.json, update portal names, and save to name.json."""
    input_json_path = 'data/filter.json'
    output_json_path = 'data/name.json'
    
    if not os.path.exists(input_json_path):
        print(f"Error: {input_json_path} not found")
        return
    
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            news_items = json.load(f)
        
        # Handle case where news_items could be a single dict or a list
        if isinstance(news_items, dict):
            news_items = [news_items]
        
        updated_news_items = []
        
        for news_item in news_items:
            url_original = news_item.get('url_original')
            if not url_original:
                print(f"Skipping news item with missing url_original: {news_item.get('titulo')}")
                continue
            
            # Get the standardized portal name from the portais table
            portal_name = get_portal_name_from_db(url_original)
            if portal_name:
                news_item['portal'] = portal_name
                print(f"Updated portal for {news_item.get('titulo')}: {portal_name}")
                updated_news_items.append(news_item)
            else:
                print(f"No matching portal found for URL: {url_original}")
                continue  # Skip if no matching portal is found
        
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
        
        # Write updated news items to name.json
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(updated_news_items, f, ensure_ascii=False, indent=4)
        print(f"Updated news items saved to {output_json_path}")
    
    except Exception as e:
        print(f"Error processing news: {e}")

if __name__ == "__main__":
    main()
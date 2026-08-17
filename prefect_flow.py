import os
from prefect import task, flow
import requests
from sentence_transformers import SentenceTransformer
import psycopg2
from pgvector.psycopg2 import register_vector
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "chatbot_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

@task
def extract_data_from_api():
    """Fetches all product data from the stable fakestoreapi.com."""
    print("Extracting data from fakestoreapi.com...")
    api_url = "https://fakestoreapi.com/products" # <-- NEW, STABLE API
    response = requests.get(api_url)
    response.raise_for_status()
    products_json = response.json()
    print(f"Extracted {len(products_json)} products.")
    return products_json

@task
def load_data_to_postgres(products_json: list):
    """Loads raw product data into the PostgreSQL database."""
    if not products_json:
        return 0
    
    print(f"Loading {len(products_json)} products into PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    register_vector(conn)
    cur = conn.cursor()
    
    # Updated query to match fakestoreapi.com's structure
    insert_query = """
    INSERT INTO products (id, title, price, description, category_name, images, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title, price = EXCLUDED.price, description = EXCLUDED.description,
        category_name = EXCLUDED.category_name, images = EXCLUDED.images,
        updated_at = EXCLUDED.updated_at, embedding = NULL;
    """
    
    now = datetime.now(timezone.utc)
    for p in products_json:
        # fakestoreapi uses 'image' not 'images' and has no timestamps, so we adjust
        cur.execute(insert_query, (
            p['id'], p['title'], p['price'], p['description'], 
            p['category'], [p['image']], now, now  # <-- MODIFIED LINE
        ))
    
    conn.commit()
    cur.close()
    conn.close()
    print("Loading complete.")
    return len(products_json)

@task
def generate_embeddings_and_update_db(products_loaded: int):
    """Finds products without embeddings, generates them, and updates the DB."""
    if products_loaded == 0:
        return

    conn = psycopg2.connect(**DB_CONFIG)
    register_vector(conn)
    cur = conn.cursor()
    
    cur.execute("SELECT id, title, description, category_name FROM products WHERE embedding IS NULL")
    products_to_embed = cur.fetchall()

    if not products_to_embed:
        print("All products are already embedded.")
        cur.close()
        conn.close()
        return
    
    print(f"Found {len(products_to_embed)} products to embed.")
    texts_to_embed = [f"Product: {p[1]}. Category: {p[3]}. Description: {p[2]}" for p in products_to_embed]
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    
    update_query = "UPDATE products SET embedding = %s WHERE id = %s"
    for i, product in enumerate(products_to_embed):
        product_id = product[0]
        embedding = embeddings[i].tolist()
        cur.execute(update_query, (embedding, product_id))
        
    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully generated and stored embeddings for {len(products_to_embed)} products.")

@flow(name="Product Sync Flow")
def product_sync_flow():
    """The main flow that orchestrates the ETL process."""
    extracted_data = extract_data_from_api()
    loaded_count = load_data_to_postgres(extracted_data)
    generate_embeddings_and_update_db(loaded_count)

if __name__ == "__main__":
    product_sync_flow()
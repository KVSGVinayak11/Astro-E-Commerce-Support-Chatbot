import os
import psycopg2
from sentence_transformers import SentenceTransformer
from pgvector.psycopg2 import register_vector
import numpy as np  # <-- 1. IMPORT NUMPY
from dotenv import load_dotenv
import config

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "chatbot_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

class RetrievalService:
    def __init__(self):
        print("Initializing PostgreSQL Retrieval Service...")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
        print("Retrieval Service initialized.")

    def retrieve_context(self, query: str, k: int = 4) -> tuple[str, str]:
        query_embedding = self.embedding_model.encode(query)
        context_str = "No context found."

        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    search_query = """
                    SELECT title, description, category_name FROM products 
                    ORDER BY embedding <-> %s::vector
                    LIMIT %s
                    """

                    # --- 2. MODIFIED LINE ---
                    # Convert the numpy array to a string representation of a list
                    embedding_str = str(query_embedding.tolist())

                    # --- 3. MODIFIED LINE ---
                    # Pass the string and the limit as parameters
                    cur.execute(search_query, (embedding_str, k))

                    results = cur.fetchall()

                    context_pieces = [f"Product: {title}. Category: {category}. Description: {description}" for title, description, category in results]

                    if context_pieces:
                        context_str = "\\n---\\n".join(context_pieces)
        except Exception as e:
            print(f"Database error during retrieval: {e}")
            return "Error retrieving data from the database.", "Database"

        return context_str, "PostgreSQL Products"
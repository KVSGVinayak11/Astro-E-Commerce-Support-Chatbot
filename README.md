# Astro — E-Commerce Support Chatbot 🤖

Astro is a Retrieval-Augmented Generation (RAG) chatbot for e-commerce customer support. It answers product questions using a PostgreSQL + pgvector knowledge base, generates responses with Google Gemini, and adapts its tone based on the detected sentiment of the user's message.

## Features

- **RAG retrieval** — Product data is embedded with `sentence-transformers` and stored in PostgreSQL via `pgvector`; the retriever finds the most relevant products for each query.
- **Sentiment-aware responses** — A `cardiffnlp/twitter-roberta-base-sentiment-latest` pipeline detects whether a query is positive, negative, or neutral, and Gemini adjusts its tone accordingly (extra empathetic on negative sentiment, enthusiastic on positive, professional on neutral).
- **LLM generation** — Uses Google's Gemini API (`google-generativeai`) to generate the final answer, grounded strictly in retrieved context.
- **Streamlit chat UI** — A simple, typing-effect chat interface (`streamlit_app.py`).
- **Prefect ETL flow** — `prefect_flow.py` pulls product data from [Fake Store API](https://fakestoreapi.com/), loads it into Postgres, and generates embeddings for any products missing them.

## Architecture

```
User query
   │
   ▼
Sentiment Analyzer (transformers) ──► sentiment label
   │
   ▼
Retriever (sentence-transformers + pgvector) ──► relevant product context
   │
   ▼
Gemini LLM (prompt = query + context + sentiment) ──► final answer
   │
   ▼
Streamlit UI
```

## Project structure

```
.
├── streamlit_app.py           # Streamlit chat UI
├── test_run.py                 # CLI script to test the chatbot without the UI
├── check_models.py             # Lists Gemini models available to your API key
├── config.py                   # Embedding/LLM model names
├── prefect_flow.py             # ETL: fetch products -> load to Postgres -> generate embeddings
├── llm/
│   └── response_generator.py   # Orchestrates sentiment + retrieval + Gemini generation
├── rag/
│   └── retriever.py            # pgvector similarity search over the products table
├── sentiment/
│   └── sentiment_analyzer.py   # RoBERTa-based sentiment classification
├── requirements.txt
├── .env.example                 # Template for required environment variables
└── .gitignore
```

## Prerequisites

- Python 3.10+
- PostgreSQL with the [`pgvector`](https://github.com/pgvector/pgvector) extension enabled
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

## Setup

1. **Clone the repo and create a virtual environment**
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in:
   - `GEMINI_API_KEY`
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

4. **Set up the database**

   Create the database and enable pgvector:
   ```sql
   CREATE DATABASE chatbot_db;
   \c chatbot_db
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

   Create the `products` table (adjust the embedding dimension to match your embedding model — `all-MiniLM-L6-v2` uses 384 dimensions):
   ```sql
   CREATE TABLE products (
       id INTEGER PRIMARY KEY,
       title TEXT,
       price NUMERIC,
       description TEXT,
       category_name TEXT,
       images TEXT[],
       embedding VECTOR(384),
       created_at TIMESTAMPTZ,
       updated_at TIMESTAMPTZ
   );
   ```

5. **Load product data and generate embeddings**
   ```bash
   python prefect_flow.py
   ```

## Running the app

**Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

**Command-line test:**
```bash
python test_run.py
```

**Check which Gemini models your key can access:**
```bash
python check_models.py
```

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | Google Gemini |
| Embeddings | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector store | PostgreSQL + pgvector |
| Orchestration | Prefect |
| Sentiment analysis | Hugging Face Transformers (`cardiffnlp/twitter-roberta-base-sentiment-latest`) |

## Security notes

- Never commit your `.env` file — it's already excluded via `.gitignore`.
- If an API key or database password was ever committed to this repo's history, rotate it immediately and consider scrubbing git history (e.g. with `git filter-repo` or BFG Repo-Cleaner).

## License

Add a license of your choice (e.g. MIT) here.

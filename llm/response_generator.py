import os
from dotenv import load_dotenv
import google.generativeai as genai
from rag.retriever import RetrievalService
from sentiment.sentiment_analyzer import SentimentAnalyzer # <-- NEW: Import the analyzer
import config

class ResponseGenerator:
    def __init__(self):
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        genai.configure(api_key=gemini_api_key)

        print(f"Initializing Generative Model '{config.LLM_MODEL_NAME}'...")
        self.model = genai.GenerativeModel(config.LLM_MODEL_NAME)
        
        # --- NEW: Initialize both services ---
        self.retriever = RetrievalService()
        self.sentiment_analyzer = SentimentAnalyzer()

        # --- NEW: Updated prompt template ---
        self.prompt_template = """
You are an expert e-commerce customer support assistant named Astro.
Your goal is to provide helpful, accurate, and emotionally appropriate answers.

INSTRUCTIONS:
1. Read the user's question and the retrieved context carefully.
2. Analyze the user's sentiment provided below.
3. Answer the user's question using ONLY the information from the context.
4. **Tailor your tone based on the user's sentiment.**
   - If the sentiment is 'negative', be extra empathetic, apologetic, and helpful.
   - If the sentiment is 'positive', be friendly and enthusiastic.
   - If the sentiment is 'neutral', maintain a polite and professional tone.
5. If the context does not contain the answer, state clearly that you don't have enough information.

USER'S SENTIMENT: {sentiment}

CONTEXT:
{context}

USER'S QUESTION:
{query}

YOUR ANSWER:
"""

    def generate_answer(self, query: str) -> dict:
        # --- NEW: Analyze sentiment first ---
        sentiment = self.sentiment_analyzer.analyze_sentiment(query)
        print(f"Detected Sentiment: {sentiment.upper()}")

        context, source_store = self.retriever.retrieve_context(query)
        
        # --- NEW: Format the prompt with sentiment ---
        complete_prompt = self.prompt_template.format(
            sentiment=sentiment, 
            context=context, 
            query=query
        )
        
        try:
            response = self.model.generate_content(complete_prompt)
            answer = response.text
        except Exception as e:
            print(f"An error occurred during LLM generation: {e}")
            answer = "I'm sorry, I encountered an issue while generating a response."
            
        return {
            "answer": answer,
            "source_store": source_store,
            "sentiment": sentiment
        }
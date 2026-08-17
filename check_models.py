import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from your .env file
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

print("Checking for available Gemini models...")

# List all models and find the ones that support 'generateContent'
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 🔐 Charger la clé API depuis .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Configuration Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# 🧠 Fonction pour interroger le modèle
def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Erreur Gemini] {e}")
        return "❌ Une erreur est survenue avec Gemini."

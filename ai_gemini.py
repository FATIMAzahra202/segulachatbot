import os
from dotenv import load_dotenv
import google.generativeai as genai

# 🔐 Charger la clé API depuis .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Configuration de l'API
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Initialisation du modèle
model = genai.GenerativeModel("models/gemini-1.5-flash")

# ✅ Fonction pour envoyer une question et recevoir une réponse
def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Erreur Gemini] {e}")
        return "❌ Une erreur est survenue en interrogeant Gemini."

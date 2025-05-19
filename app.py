import streamlit as st
from dotenv import load_dotenv
from ai_gemini import ask_gemini
import base64
import os
from datetime import datetime
import pandas as pd
import re

load_dotenv()

# Initialisation session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Fonction pour afficher le logo
def show_logo(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style='text-align:center; margin:10px 0;'>
                <img src='data:image/jpeg;base64,{encoded}' style='width:180px;' alt='SEGULA Logo'>
            </div>
        """, unsafe_allow_html=True)

# Nettoyage texte (normalisation)
def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# FAQs
base_faq_fr = {
    "quels sont les horaires de travail": "Les horaires standards sont de 9h à 17h du lundi au vendredi.",
    "comment poser un congé": "Vous devez faire la demande via l’intranet RH ou contacter votre manager.",
    "quels sont les avantages sociaux": "SEGULA offre mutuelle, transport, tickets resto, etc."
}
base_faq_en = {
    "what are the working hours": "Standard hours are 9 AM to 5 PM, Monday to Friday.",
    "how to request a leave": "You must submit the request via the HR intranet or contact your manager.",
    "what are the social benefits": "SEGULA offers health insurance, transportation, meal vouchers, etc."
}

# 📥 Sauvegarde Excel
def save_to_excel(messages):
    df = pd.DataFrame([
        {"Role": m["role"], "Message": m["content"], "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for m in messages
    ])
    df.to_excel("chat_log.xlsx", index=False)

def download_excel_button():
    if os.path.exists("chat_log.xlsx"):
        with open("chat_log.xlsx", "rb") as file:
            st.download_button("📥 Télécharger l'historique", file, file_name="chat_log.xlsx")

# Configuration de la page
st.set_page_config(page_title="Chat RH SEGULA", layout="centered")

# Langue
lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "English"])
faq_base = base_faq_fr if lang == "Français" else base_faq_en

# Interface
if lang == "Français":
    show_logo("SEGULA_Technologies_logo_DB.jpg")
    st.markdown("<h2 style='text-align:center;color:#1e88e5;'>🤖 Chatbot RH SEGULA Technologies</h2>", unsafe_allow_html=True)
    welcome = "Bienvenue ! Posez vos questions RH ici."
    input_placeholder = "Tapez votre message ici..."
    label_user = "👩‍💼 Vous"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Vider la conversation"
else:
    show_logo("SEGULA_Technologies_logo_DB.jpg")
    st.markdown("<h2 style='text-align:center;color:#1e88e5;'>🤖 SEGULA HR Chatbot</h2>", unsafe_allow_html=True)
    welcome = "Welcome! Ask your HR questions here."
    input_placeholder = "Type your message here..."
    label_user = "👩‍💼 You"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Clear conversation"

st.markdown(f"<p style='text-align:center;'>{welcome}</p>", unsafe_allow_html=True)

# 🔁 Réinitialisation
if st.button(clear_btn):
    st.session_state.messages = []
    if os.path.exists("chat_log.xlsx"):
        os.remove("chat_log.xlsx")
    st.rerun()

# 🧠 Traitement du message
if st.session_state.submitted:
    user_msg = st.session_state.user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_msg})

    # Vérifie dans FAQ
    clean = normalize(user_msg)
    matched = None
    for q in faq_base:
        if normalize(q) == clean:
            matched = faq_base[q]
            break

    if matched:
        response = matched
    else:
        try:
            response = ask_gemini(user_msg)
        except Exception:
            response = "❌ Une erreur est survenue." if lang == "Français" else "❌ An error occurred."

    st.session_state.messages.append({"role": "bot", "content": response})
    save_to_excel(st.session_state.messages)
    st.session_state.submitted = False
    st.session_state.user_input = ""

# 💬 Affichage des messages
with st.container():
    for msg in st.session_state.messages:
        align = "margin-left:auto;" if msg["role"] == "user" else "margin-right:auto;"
        bg = "#1e88e5" if msg["role"] == "user" else "#f1f1f1"
        color = "#fff" if msg["role"] == "user" else "#000"
        label = label_user if msg["role"] == "user" else label_bot
        st.markdown(f"""
            <div style='background:{bg};color:{color};padding:10px 15px;border-radius:12px;
                        margin:10px 0;max-width:75%;{align}'>
                {label}: {msg['content']}
            </div>
        """, unsafe_allow_html=True)

# ✅ Input en bas
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder=input_placeholder)
    submitted = st.form_submit_button("Envoyer")

if submitted and user_input:
    st.session_state.user_input = user_input
    st.session_state.submitted = True
    st.rerun()

# 📥 Bouton historique
download_excel_button()

# 🔽 Scroll auto
st.markdown("""
    <script>
        var chatDiv = window.parent.document.querySelector('.main');
        if (chatDiv) {
            chatDiv.scrollTo(0, chatDiv.scrollHeight);
        }
    </script>
""", unsafe_allow_html=True)

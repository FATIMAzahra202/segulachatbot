import streamlit as st
from dotenv import load_dotenv
import base64
import os
from datetime import datetime
import pandas as pd
from ai_gemini import ask_gemini

# Charger les variables d’environnement
load_dotenv()

# Configurer la page
st.set_page_config(page_title="Chat RH SEGULA", layout="centered")

# Initialiser session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Fonction pour afficher le logo
def show_logo(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
            <div style='text-align:center; margin:10px 0;'>
                <img src='data:image/png;base64,{encoded}' style='width:180px;' alt='Logo SEGULA'>
            </div>
        """, unsafe_allow_html=True)

# Sauvegarder l'historique dans un fichier Excel
def save_to_excel(messages):
    data = [
        {"Rôle": m["role"], "Message": m["content"], "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for m in messages
    ]
    df = pd.DataFrame(data)
    df.to_excel("chat_log.xlsx", index=False)

# Bouton pour télécharger le fichier Excel
def download_excel_button():
    if os.path.exists("chat_log.xlsx"):
        with open("chat_log.xlsx", "rb") as f:
            st.download_button("📥 Télécharger l'historique", f, file_name="chat_log.xlsx")

# Choix de la langue
lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "English"])
st.session_state.lang = lang  # pour l'utiliser dans toute l’app

# Interface multilingue
if lang == "Français":
    show_logo("SEGULA_Technologies_logo_DB.jpg")
    st.markdown("<h2 style='text-align:center;color:#1e88e5;'>🤖 Chatbot RH SEGULA Technologies</h2>", unsafe_allow_html=True)
    input_placeholder = "Tapez votre message ici..."
    label_user = "👩‍💼 Vous"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Vider la conversation"
else:
    show_logo("SEGULA_Technologies_logo_DB.jpg")
    st.markdown("<h2 style='text-align:center;color:#1e88e5;'>🤖 SEGULA HR Chatbot</h2>", unsafe_allow_html=True)
    input_placeholder = "Type your message here..."
    label_user = "👩‍💼 You"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Clear conversation"

# Bouton pour vider la session
if st.button(clear_btn):
    st.session_state.messages = []
    if os.path.exists("chat_log.xlsx"):
        os.remove("chat_log.xlsx")
    st.rerun()

# Affichage des messages
with st.container():
    for msg in st.session_state.messages:
        align = "margin-left:auto;" if msg["role"] == "user" else "margin-right:auto;"
        bg = "#1e88e5" if msg["role"] == "user" else "#f1f1f1"
        color = "#fff" if msg["role"] == "user" else "#000"
        label = label_user if msg["role"] == "user" else label_bot
        st.markdown(f"""
            <div style='background:{bg};color:{color};padding:10px 15px;
                        border-radius:12px;margin:10px 0;max-width:75%;{align}'>
                {label}: {msg['content']}
            </div>
        """, unsafe_allow_html=True)

# Formulaire d'envoi
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder=input_placeholder)
    submitted = st.form_submit_button("Envoyer")

# Traitement du message
if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        response = ask_gemini(user_input)
    except Exception as e:
        response = "❌ Une erreur est survenue avec Gemini." if lang == "Français" else "❌ An error occurred with Gemini."

    st.session_state.messages.append({"role": "bot", "content": response})
    save_to_excel(st.session_state.messages)
    st.rerun()

# Bouton téléchargement Excel
download_excel_button()

# Scroll automatique vers le bas
st.markdown("""
    <script>
        var chatDiv = window.parent.document.querySelector('.main');
        if (chatDiv) {
            chatDiv.scrollTo(0, chatDiv.scrollHeight);
        }
    </script>
""", unsafe_allow_html=True)

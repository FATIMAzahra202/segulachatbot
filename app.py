import streamlit as st
from dotenv import load_dotenv
import os
import base64
import pandas as pd
import tempfile
import fitz  # PyMuPDF
from datetime import datetime
import re
from ai_gemini import ask_gemini

load_dotenv()
st.set_page_config(page_title="Chat RH SEGULA", layout="centered")

# FAQ locale
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

# États init
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_content" not in st.session_state:
    st.session_state.doc_content = ""

# Sélection langue
lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "English"])
faq = base_faq_fr if lang == "Français" else base_faq_en

# Textes UI
if lang == "Français":
    title = "🤖 Chatbot RH SEGULA Technologies"
    input_placeholder = "Tapez votre message ici..."
    label_user = "👩‍💼 Vous"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Vider la conversation"
    upload_label = "📎 Téléverser un document (PDF ou TXT)"
else:
    title = "🤖 SEGULA HR Chatbot"
    input_placeholder = "Type your message here..."
    label_user = "👩‍💼 You"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Clear conversation"
    upload_label = "📎 Upload a document (PDF or TXT)"

# Logo
def show_logo(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"<div style='text-align:center'><img src='data:image/png;base64,{encoded}' width='180'></div>", unsafe_allow_html=True)

show_logo("SEGULA_Technologies_logo_DB.jpg")
st.markdown(f"<h2 style='text-align:center; color:#1e88e5;'>{title}</h2>", unsafe_allow_html=True)

# Reset chat
if st.button(clear_btn):
    st.session_state.messages = []
    st.session_state.doc_content = ""
    if os.path.exists("chat_log.xlsx"):
        os.remove("chat_log.xlsx")
    st.rerun()

# Upload document sécurisé
uploaded_file = st.file_uploader(upload_label, type=["pdf", "txt"])
if uploaded_file:
    file_ext = uploaded_file.name.split(".")[-1].lower()
    if file_ext == "txt":
        st.session_state.doc_content = uploaded_file.read().decode("utf-8")
        st.success(f"✅ Fichier TXT chargé : {uploaded_file.name}")
    elif file_ext == "pdf":
        pdf_bytes = uploaded_file.read()
        if pdf_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_bytes)
                tmp.flush()
                try:
                    with fitz.open(tmp.name) as doc:
                        text = ""
                        for page in doc:
                            text += page.get_text()
                        st.session_state.doc_content = text
                        st.success(f"✅ Fichier PDF chargé : {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ Erreur lors de la lecture du PDF : {e}")
                finally:
                    os.unlink(tmp.name)
        else:
            st.warning("⚠️ Le fichier PDF est vide ou invalide.")

# Affichage des messages
for msg in st.session_state.messages:
    align = "margin-left:auto;" if msg["role"] == "user" else "margin-right:auto;"
    bg = "#1e88e5" if msg["role"] == "user" else "#f1f1f1"
    color = "#fff" if msg["role"] == "user" else "#000"
    label = label_user if msg["role"] == "user" else label_bot
    st.markdown(f"""
        <div style='background:{bg}; color:{color}; padding:10px 15px;
                    border-radius:12px; margin:10px 0; max-width:75%; {align}'>
            {label}: {msg['content']}
        </div>
    """, unsafe_allow_html=True)

# Normalisation
def normalize(text):
    return re.sub(r"[^\w\s]", "", text.lower().strip())

# Formulaire
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder=input_placeholder)
    submitted = st.form_submit_button("Envoyer")

if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    clean_input = normalize(user_input)

    # Priorité : base locale > document > Gemini
    matched = None
    for q in faq:
        if normalize(q) == clean_input:
            matched = faq[q]
            break

    if matched:
        response = matched
    elif st.session_state.doc_content:
        prompt = f"""
Voici un document RH :

\"\"\"
{st.session_state.doc_content}
\"\"\"

Réponds à cette question : {user_input}
"""
        response = ask_gemini(prompt)
    else:
        response = ask_gemini(user_input)

    st.session_state.messages.append({"role": "bot", "content": response})

    # Log Excel
    df = pd.DataFrame([
        {"Role": m["role"], "Message": m["content"], "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for m in st.session_state.messages
    ])
    df.to_excel("chat_log.xlsx", index=False)
    st.rerun()

# Bouton téléchargement Excel
if os.path.exists("chat_log.xlsx"):
    with open("chat_log.xlsx", "rb") as f:
        st.download_button("📥 Télécharger l'historique", f, file_name="chat_log.xlsx")

# Scroll auto JS
st.markdown("""
<script>
    var chatDiv = window.parent.document.querySelector('.main');
    if (chatDiv) {
        chatDiv.scrollTo(0, chatDiv.scrollHeight);
    }
</script>
""", unsafe_allow_html=True)

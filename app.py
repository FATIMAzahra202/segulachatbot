import streamlit as st
from dotenv import load_dotenv
from ai_gemini import ask_gemini
import base64
import os
from datetime import datetime
import pandas as pd


load_dotenv()


base_faq_fr = {
    "Quels sont les horaires de travail ?": "Les horaires standards sont de 9h à 17h du lundi au vendredi.",
    "Comment poser un congé ?": "Vous devez faire la demande via l’intranet RH ou contacter votre manager.",
    "Quels sont les avantages sociaux ?": "SEGULA offre mutuelle, transport, tickets resto, etc."
}
base_faq_en = {
    "What are the working hours?": "Standard hours are 9 AM to 5 PM, Monday to Friday.",
    "How to request a leave?": "You must submit the request via the HR intranet or contact your manager.",
    "What are the social benefits?": "SEGULA offers health insurance, transportation, meal vouchers, etc."
}


if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False


if st.session_state.submitted:
    question = st.session_state.user_input.strip()
    st.session_state.messages.append({"role": "user", "content": question})
    if question in st.session_state.faq_base:
        response = st.session_state.faq_base[question]
    else:
        try:
            response = ask_gemini(question)
        except Exception:
            response = "❌ Une erreur est survenue. Veuillez réessayer." if st.session_state.lang == "Français" else "❌ An error occurred. Please try again."
    st.session_state.messages.append({"role": "bot", "content": response})
    df = pd.DataFrame([
        {"Role": m["role"], "Message": m["content"], "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for m in st.session_state.messages
    ])
    df.to_excel("chat_log.xlsx", index=False)
    st.session_state.user_input = ""
    st.session_state.submitted = False


def show_logo(path):
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style='text-align:center;margin:10px 0;'>
                <img src='data:image/jpeg;base64,{encoded}' style='width:200px;' alt='SEGULA Logo'>
            </div>
        """, unsafe_allow_html=True)


def download_excel_button():
    if os.path.exists("chat_log.xlsx"):
        with open("chat_log.xlsx", "rb") as file:
            st.download_button("📥 Télécharger l'historique", file, file_name="chat_log.xlsx")

# ✅ Configuration de page
st.set_page_config(page_title="Chat RH SEGULA", layout="centered")

# ✅ Langue
st.session_state.lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "English"])
st.session_state.faq_base = base_faq_fr if st.session_state.lang == "Français" else base_faq_en

# ✅ Interface multilingue
if st.session_state.lang == "Français":
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


if st.button(clear_btn):
    st.session_state.messages = []
    if os.path.exists("chat_log.xlsx"):
        os.remove("chat_log.xlsx")
    st.experimental_rerun()

# ✅ Affichage messages
with st.container():
    for msg in st.session_state.messages:
        align = "margin-left:auto;" if msg["role"] == "user" else "margin-right:auto;"
        bg = "#1e88e5" if msg["role"] == "user" else "#f1f1f1"
        color = "#fff" if msg["role"] == "user" else "#000"
        icon = label_user if msg["role"] == "user" else label_bot
        st.markdown(f"""
            <div style='background:{bg};color:{color};padding:10px 15px;
            border-radius:12px;margin:10px 0;max-width:75%;{align}'>
                {icon}: {msg['content']}
            </div>
        """, unsafe_allow_html=True)

# ✅ Input toujours visible
with st.empty().form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder=input_placeholder)
    submit_button = st.form_submit_button("Envoyer")

if submit_button and user_input:
    st.session_state.user_input = user_input
    st.session_state.submitted = True


download_excel_button()


st.markdown("""
    <script>
        var chatDiv = window.parent.document.querySelector('.main');
        if (chatDiv) {
            chatDiv.scrollTo(0, chatDiv.scrollHeight);
        }
    </script>
""", unsafe_allow_html=True)

import streamlit as st
from dotenv import load_dotenv
import openai
import base64
import os
from datetime import datetime
import pandas as pd

# Charger .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration page
st.set_page_config(page_title="Chat RH SEGULA", layout="centered")

# Initialiser session
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔹 Logo
def show_logo(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
            <div style='text-align:center; margin:10px 0;'>
                <img src='data:image/jpeg;base64,{encoded}' style='width:180px;' alt='SEGULA Logo'>
            </div>
        """, unsafe_allow_html=True)

# 🔹 Exporter historique
def save_to_excel(messages):
    data = [
        {"Rôle": m["role"], "Message": m["content"], "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        for m in messages
    ]
    df = pd.DataFrame(data)
    df.to_excel("chat_log.xlsx", index=False)

def download_excel_button():
    if os.path.exists("chat_log.xlsx"):
        with open("chat_log.xlsx", "rb") as f:
            st.download_button("📥 Télécharger l'historique", f, file_name="chat_log.xlsx")

# 🌍 Langue
lang = st.sidebar.selectbox("🌐 Langue / Language", ["Français", "English"])

# 🧠 FAQ interne
faq_fr = {
    "quels sont les horaires de travail": "Les horaires standards sont de 9h à 17h du lundi au vendredi.",
    "comment poser un congé": "Vous devez faire la demande via l’intranet RH ou contacter votre manager.",
    "quels sont les avantages sociaux": "SEGULA offre mutuelle, transport, tickets resto, etc."
}

faq_en = {
    "what are the working hours": "Standard hours are 9 AM to 5 PM, Monday to Friday.",
    "how to request a leave": "You must submit the request via the HR intranet or contact your manager.",
    "what are the social benefits": "SEGULA offers health insurance, transportation, meal vouchers, etc."
}

# 📋 Interface
if lang == "Français":
    show_logo("SEGULA_Technologies_logo_DB.jpg")
    st.markdown("<h2 style='text-align:center;color:#1e88e5;'>🤖 Chatbot RH SEGULA Technologies</h2>", unsafe_allow_html=True)
    input_placeholder = "Tapez votre message ici..."
    label_user = "👩‍💼 Vous"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Vider la conversation"
    faq = faq_fr
else:
    show_logo("SEGULA_Technologies_logo_DB.jpg")
    st.markdown("<h2 style='text-align:center;color:#1e88e5;'>🤖 SEGULA HR Chatbot</h2>", unsafe_allow_html=True)
    input_placeholder = "Type your message here..."
    label_user = "👩‍💼 You"
    label_bot = "🤖 Bot"
    clear_btn = "🗑️ Clear conversation"
    faq = faq_en

# 🧹 Clear chat
if st.button(clear_btn):
    st.session_state.messages = []
    if os.path.exists("chat_log.xlsx"):
        os.remove("chat_log.xlsx")
    st.rerun()


# 💬 Afficher messages
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

# ✅ Formulaire
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder=input_placeholder)
    submitted = st.form_submit_button("Envoyer")

# 🔁 Traitement du message
if submitted and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    msg_clean = user_input.strip().lower()

    # ➤ 1. Réponse depuis FAQ locale
    if msg_clean in faq:
        response = faq[msg_clean]
    else:
        # ➤ 2. Appel OpenAI si non trouvé
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant RH de l'entreprise SEGULA."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=200,
                temperature=0.7
            )
            response = completion.choices[0].message.content.strip()
        except Exception as e:
            response = "❌ Une erreur est survenue avec OpenAI."

    st.session_state.messages.append({"role": "bot", "content": response})
    save_to_excel(st.session_state.messages)
    st.rerun()

# 📥 Télécharger historique
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

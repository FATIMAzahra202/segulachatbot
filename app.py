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
    "je viens d'arriver chez Segula partir de quand puis-je prendre mes congés payés ?": "Chez Segula Maroc, tu peux prendre tes congés payés après 6 mois de travail effectif. Tu les acquiers progressivement dès ton arrivée, à raison de 1,5 jour ouvrable par mois, mais tu pourras les utiliser à partir de 6 mois d’ancienneté",
    "Je viens d'intégrer Segula quels sont mes droits en congés payés ?": "Chez Segula Maroc, tu commences à acquérir des jours de congé dès ton arrivée, à raison de 1,5 jour ouvrable par mois de travail effectif, soit environ 18 jours ouvrables par an. En revanche, tu pourras commencer à les poser après 6 mois de travail effectif, sauf cas exceptionnel validé par ta hiérarchie.",
    "Comment puis-je bénéficier d’un congé payé ?": "Pour bénéficier d’un congé payé chez Segula Maroc, il te suffit de soumettre ta demande via la plateforme HRMAPS, en précisant les dates souhaitées. La demande doit être faite au minimum 7 jours avant la date de départ, et elle doit être validée par ton manager.",
    "Je suis Manager, je souhaite traiter les congés de mes collaborateurs. Comment dois je m'y prendre ?": "En tant que manager, dès qu’un collaborateur soumet une demande de congé via HRMAPS,👉 tu reçois automatiquement une notification par e-mail t’informant qu’une demande est en attente de traitement. Pour y répondre :Connecte-toi à la plateforme HRMAPS, Accède à l’onglet “Congés”, Consulte les détails de la demande (dates, solde, remarques),Puis valide ou refuse la demande selon les besoins de l’équipe, en ajoutant si besoin un commentaire. ✅ Il est important de traiter la demande rapidement afin de permettre au collaborateur d’organiser son absence.⚠️ Pense à vérifier la continuité du service pour éviter les absences simultanées non planifiées.",
    "Pourrai-je cumuler mes congés payés d’une année sur l’autre ?": "Oui, les congés payés peuvent être cumulés, mais dans la limite de 2 années maximum.Cela signifie que tu dois utiliser tes congés dans un délai de 24 mois à partir de leur acquisition, sinon ils seront perdus.",
    "J'ai un solde de congé important, mon manager me presse de prendre un congé. Pourquoi ?": "Ton manager t’encourage à prendre tes congés pour deux raisons principales :Il est important de se reposer régulièrement pour préserver ton bien-être, maintenir ta motivation et ton efficacité au travail. Les congés ne sont pas un luxe, mais un droit conçu pour équilibrer vie professionnelle et personnelle.les congés payés ont une durée de validité limitée. Selon la réglementation en vigueur chez Segula Maroc, les congés peuvent être cumulés sur une période de 2 ans maximum.👉 Au-delà de ce délai, les jours non pris sont perdus, sauf cas exceptionnels.Ton manager veille donc à ce que tu ne perdes pas tes droits et à ce que tu puisses profiter pleinement de ton solde avant expiration.",
    "Mon congé payé a été refusé, puis-je demander un congé sans solde?": "Avant de faire une demande de congé sans solde, il est important de comprendre la raison du refus de ton congé payé. Commence par consulter ton solde de congés sur la plateforme HRMAPS, où tu as une visibilité en temps réel de tes droits acquis.Si ton solde est suffisant mais que ta demande a été refusée, il est essentiel de contacter ton manager pour comprendre si ce refus est lié à un contexte opérationnel, comme une charge de travail importante ou une organisation spécifique de l’équipe.Si ton solde est insuffisant ou si tu constates une anomalie, n’hésite pas à contacter la responsable paie pour clarifier ta situation.Une fois la situation éclaircie et avec l’accord de ton manager, tu pourras envisager une demande de congé sans solde.Le plus important est de communiquer directement avec les personnes concernées pour comprendre la raison du refus et trouver la meilleure solution adaptée à ta situation.",
    "Comment puis-je demander un congé sans solde ? Quelle est la démarche à suivre ?": "La démarche pour demander un congé sans solde est la même que pour un congé payé.Tu dois soumettre ta demande via la plateforme HRMAPS, en précisant clairement qu’il s’agit d’un congé sans solde.Pense à faire ta demande au moins 7 jours avant la date souhaitée et attendre la validation de ton manager avant de finaliser ton organisation.N’oublie pas que la prise d’un congé sans solde reste soumise à l’accord de ton manager.",
    "J'ai droit à combien de jour de congé par an ?": "Si ton ancienneté est inférieure à 2 ans, tu acquiers 1,5 jour ouvrable de congé par mois travaillé, soit environ 18 jours ouvrables par an.Si ton ancienneté est égale ou supérieure à 2 ans, ce droit passe à 2 jours ouvrables par mois travaillé, soit environ 24 jours ouvrables par an. Pour connaître précisément ton solde de congés disponible, tu peux le consulter directement sur la plateforme HRMAPS, qui te donne une visibilité en temps réel sur tes droits acquis.",
    "Je suis enceinte, quelle démarche dois-je engager auprès de mon​ employeur ?": "Selon le Code du travail marocain, dès que tu as connaissance de ta grossesse, tu dois :Informer ton employeur rapidement, idéalement par écrit, pour lui permettre de prendre les mesures nécessaires.Fournir un certificat médical attestant ta grossesse délivré par ton médecin. Cette notification permet à l’employeur de te protéger conformément à la loi.Par ailleurs, tu bénéficies d’un congé de maternité obligatoire de 14 semaines, réparti avant et après l’accouchement. Ce congé est un droit protégé par la loi et garantit la suspension de ton contrat de travail pendant cette période. N’hésite pas à te rapprocher du service RH pour formaliser ces démarches et bénéficier d’un accompagnement personnalisé.",
    "Quelles sont les démarches que je dois accomplir pour bénéficier de mon congé de maternité ?": "Pour bénéficier de ton congé de maternité conformément à la législation marocaine, voici les principales étapes à suivre : Informer ton employeur dès que possible, idéalement par écrit (mail ou lettre), en précisant la date prévue d’accouchement. Fournir un certificat médical délivré par un professionnel de santé attestant ta grossesse et la date présumée de l’accouchement. Déclarer ta grossesse à la Caisse Nationale de Sécurité Sociale (CNSS) si tu es affiliée, en envoyant le certificat médical dans les délais requis pour bénéficier des indemnités journalières de maternité.Planifier ton congé maternité avec ton employeur et le service RH, afin d’organiser la suspension temporaire de ton contrat de travail pendant la durée légale de 14 semaines.Pendant ton congé, tu perçois des indemnités journalières de maternité versées par la CNSS, sous réserve d’avoir rempli les conditions d’affiliation.",
    "Commemt suis-je rémunérée durant mon congé de maternité ?": "Pendant ton congé maternité, tu ne perçois pas ton salaire, mais une indemnité journalière versée par la CNSS. Elle correspond à 100 % de ton salaire brut moyen des 6 derniers mois, Plafonnée à 6 000 dirhams par mois, soit environ 19 600 DH pour 14 semaines. Pour en bénéficier, tu dois : Avoir au moins 54 jours de cotisations à la CNSS dans les 10 derniers mois,Déposer un dossier complet (certificat médical, attestation de congé, bulletins de paie) à la CNSS.",
    "Quels  sont les critères d'éligibilté  pour qu'une femme enceinte bénéficie des indemnités journalières de maternité ?": "Pendant ton congé maternité, tu ne perçois pas ton salaire, mais une indemnité journalière versée par la CNSS.Elle correspond à 100 % de ton salaire brut moyen des 6 derniers mois,Plafonnée à 6 000 dirhams par mois, soit environ 19 600 DH pour 14 semaines. Pour en bénéficier, tu dois :Avoir au moins 54 jours de cotisations à la CNSS dans les 10 derniers mois,Déposer un dossier complet (certificat médical, attestation de congé, bulletins de paie) à la CNSS.",
    "​Quelles sont les pièces à fournir pour bénéficier des indemnités journalières de maternité ?": "Pour bénéficier des indemnités journalières de maternité versées par la CNSS, tu dois fournir un dossier complet dans un délai maximum de 30 jours à compter de la date de ton accouchement.Pièces à fournir :Certificat médical de grossesse, précisant la date présumée de l’accouchement, Acte d’accouchement (à fournir après la naissance), Attestation de congé maternité signée par l’employeur, indiquant les dates exactes du congé,Bulletins de paie des 6 derniers mois,Formulaire de demande d’indemnité de maternité (disponible sur www.cnss.ma ou dans une agence CNSS),Relevé d’identité bancaire (RIB) au nom de l’assurée.Délai à respecter : Le dossier doit être déposé dans les 30 jours suivant la date de l’accouchement.Un retard dans le dépôt peut entraîner le refus du remboursement.",
    "Auprès de quel service je peux me procurer les imprimés relatifs à la demande des indemnités journalières de ​​maternité ?​": "Où se procurer les imprimés ?En ligne : Télécharge le formulaire intitulé « Avis d’interruption de travail et demande d’indemnités journalières » directement sur le site officiel de la CNSS : www.cnss.maEn agence CNSS : Rends-toi à l’agence CNSS la plus proche pour obtenir une version papier du formulaire.",
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

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()
os.environ["PYTHONIOENCODING"] = "utf-8"

from agent import traiter_ticket

st.set_page_config(
    page_title="Support IT — Portail employé",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Portail Support IT")
st.markdown("Bienvenue sur le portail de support informatique. Décrivez votre problème ci-dessous, notre équipe vous répondra dans les plus brefs délais.")

st.divider()

with st.form("ticket_form"):
    employe = st.text_input("Votre nom", placeholder="ex: Alice Bernard")
    email = st.text_input("Votre email professionnel", placeholder="ex: alice.bernard@entreprise.fr")
    priorite = st.selectbox("Niveau d'urgence", ["Basse", "Moyenne", "Haute", "Bloquant"])
    description = st.text_area("Décrivez votre problème", placeholder="Ex: Je n'arrive pas à me connecter à mon VPN depuis ce matin...", height=150)
    submitted = st.form_submit_button("📨 Envoyer ma demande")

if submitted and employe and description and email:
    with st.spinner("Votre demande est en cours de traitement..."):
        resultat = traiter_ticket(employe, description, priorite)

    st.divider()

    if resultat["escalade"]:
        st.warning("### Votre demande a bien été enregistrée")
        st.markdown(f"""
Bonjour **{employe}**,

Votre demande a été transmise à notre équipe technique qui vous contactera dans les plus brefs délais.

Un email de confirmation a été envoyé à **{email}**.

> **Référence :** TK-{employe.replace(' ', '').upper()[:6]}
> **Urgence :** {priorite}
> **Délai de prise en charge estimé :** 2 heures
        """)
    else:
        st.success("### Votre problème a été résolu automatiquement")
        reponse_propre = resultat["reponse"].replace("REPONSE_AUTO:", "").replace("RÉPONSE_AUTO:", "").strip()
        st.markdown(f"""
Bonjour **{employe}**,

{reponse_propre}

---
*Un email de confirmation a été envoyé à **{email}**.*
        """)

elif submitted:
    st.error("Veuillez remplir tous les champs avant d'envoyer.")

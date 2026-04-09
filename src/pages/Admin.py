import streamlit as st
import json
import pandas as pd

st.set_page_config(
    page_title="SmartDesk — Admin",
    page_icon="🟣",
    layout="wide"
)

st.title("🟣 SmartDesk — Dashboard Admin")
st.caption("Vue réservée aux administrateurs du support IT")

def charger_logs():
    try:
        with open("data/tickets_log.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

logs = charger_logs()

if logs:
    df = pd.DataFrame(logs)

    total = len(df)
    escalades = int(df["escalade"].sum())
    auto = total - escalades
    taux_auto = round((auto / total) * 100, 1) if total > 0 else 0

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total tickets", total)
    col2.metric("Reponses auto", auto)
    col3.metric("Escalades", escalades)
    col4.metric("Taux automatisation", f"{taux_auto}%")

    st.divider()

    # Graphiques
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Repartition par priorite")
        st.bar_chart(df["priorite"].value_counts())

    with col2:
        st.subheader("Escalades vs Reponses auto")
        st.bar_chart(df["escalade"].map({True: "Escalade", False: "Reponse auto"}).value_counts())

    st.divider()

    # Historique complet
    st.subheader("Historique complet des tickets")
    df_display = df[["id", "date", "employe", "priorite", "escalade", "faq_consultee"]].copy()
    df_display["escalade"] = df_display["escalade"].map({True: "Escalade", False: "Auto"})
    df_display["faq_consultee"] = df_display["faq_consultee"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
    df_display.columns = ["ID", "Date", "Employe", "Priorite", "Statut", "FAQ consultee"]
    st.dataframe(df_display, use_container_width=True)

    # Tickets escaladés uniquement
    st.divider()
    st.subheader("Tickets escalades — Action requise")
    df_escalades = df[df["escalade"] == True][["id", "date", "employe", "priorite", "description"]].copy()
    if not df_escalades.empty:
        df_escalades.columns = ["ID", "Date", "Employe", "Priorite", "Description"]
        st.dataframe(df_escalades, use_container_width=True)
    else:
        st.success("Aucun ticket escalade pour le moment.")

else:
    st.info("Aucun ticket traite pour le moment.")

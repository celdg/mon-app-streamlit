import streamlit as st

st.set_page_config(page_title="Mon App Mobile", page_icon="📱")

st.title("📱 Mon Application")
st.write("Félicitations ! Votre application fonctionne.")

nom = st.text_input("Entrez votre prénom :")
if nom:
    st.success(f"Bonjour {nom} ! Bienvenue sur votre application mobile.")
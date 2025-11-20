import streamlit as st

if st.button("Afficher une notification"):
    st.toast("Opération réussie !", icon="✅")
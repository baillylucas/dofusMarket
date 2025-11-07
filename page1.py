import streamlit as st
import requests
import json
from datetime import datetime
# st.session_state.my_var : données internes à un utilisateur
# st.cache_date et st.cache_ressource : données partagées entre utilisateurs

# Configuration de la page
st.set_page_config(page_title="Mon App", page_icon="🎈")

# ===== Cache avec bouton de rafraîchissement manuel =====
@st.cache_data(ttl=3600)
def load_data_with_manual_refresh(file_id):
    """Cache de 1h avec possibilité de forcer le rafraîchissement"""
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# ID de votre fichier Google Drive
FILE_ID = '1qO5ZaWX6xJLH70Kih3oO73NKTdUHuRcO'

# Main page content 
st.markdown("# Main page 🎈")
st.sidebar.markdown("# Main page 🎈")

# Cache avec bouton de rafraîchissement
st.info("⏱️ Mode : Cache 1h avec bouton de rafraîchissement")

# Bouton pour forcer le rafraîchissement
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 Rafraîchir", type="primary"):
        st.cache_data.clear()
        st.rerun()

try:
    data = load_data_with_manual_refresh(FILE_ID)
    st.success("Données en cache (cliquez sur 'Rafraîchir' pour recharger)")
except Exception as e:
    st.error(f"Erreur : {e}")
    data = None

# Afficher les données si chargées avec succès
if data:
    # Timestamp du chargement
    st.caption(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")
    
    # Afficher les informations utilisateur
    if 'utilisateur' in data:
        st.subheader("Informations Utilisateur")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Nom :** {data['utilisateur']['nom']}")
            st.write(f"**Prénom :** {data['utilisateur']['prenom']}")
            st.write(f"**Email :** {data['utilisateur']['email']}")
        
        with col2:
            st.write(f"**Âge :** {data['utilisateur']['age']}")
            st.write(f"**Actif :** {'✅' if data['utilisateur']['actif'] else '❌'}")
    
    # Afficher l'adresse
    if 'adresse' in data:
        st.subheader("Adresse")
        st.write(f"{data['adresse']['rue']}, {data['adresse']['code_postal']} {data['adresse']['ville']}, {data['adresse']['pays']}")
    
    # Afficher les compétences
    if 'competences' in data:
        st.subheader("Compétences")
        st.write(", ".join(data['competences']))
    
    # Afficher les projets
    if 'projets' in data:
        st.subheader("Projets")
        for projet in data['projets']:
            with st.expander(f"{projet['nom']} - {projet['statut']}"):
                st.write(f"**Date de début :** {projet['date_debut']}")
                st.write(f"**Statut :** {projet['statut']}")
    
    # Afficher le JSON brut dans la sidebar
    with st.sidebar:
        st.subheader("Données brutes")
        if st.checkbox("Afficher JSON"):
            st.json(data)
else:
    st.warning("Impossible de charger les données.")

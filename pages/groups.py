import streamlit as st
import pandas as pd
from utils import (
    get_user_groups, create_group, delete_group, load_groups_data, save_groups_data
)
from config import CURRENT_USER

# Configuration
st.set_page_config(layout="wide")

st.markdown("# 👥 Gestion des Groupes")

# Charger les groupes de l'utilisateur
user_groups = get_user_groups()

# Afficher les statistiques
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Mes groupes", sum(1 for g in user_groups.values() if g['owner'] == CURRENT_USER))
with col2:
    st.metric("Groupes partagés avec moi", sum(1 for g in user_groups.values() if g['owner'] != CURRENT_USER))
with col3:
    st.metric("Total", len(user_groups))

st.markdown("---")

# Section Créer un nouveau groupe
st.markdown("## ➕ Créer un nouveau groupe")

with st.form("create_group_form"):
    col_name, col_shared = st.columns([2, 2])

    with col_name:
        new_group_name = st.text_input("Nom du groupe", key="form_new_group_name")

    with col_shared:
        # Récupérer la liste de tous les utilisateurs
        groups_data = load_groups_data()
        all_users = [u for u in groups_data.get('users', []) if u != CURRENT_USER]
        shared_users = st.multiselect(
            "Partager avec",
            options=all_users,
            key="form_shared_users"
        )

    submit_create = st.form_submit_button("Créer le groupe", use_container_width=True)

    if submit_create:
        if new_group_name:
            group_id = create_group(new_group_name, shared_users)
            if group_id:
                # Invalider le cache
                st.cache_data.clear()
                st.success(f"✓ Groupe '{new_group_name}' créé avec succès")
                st.rerun()
            else:
                st.error("✗ Erreur lors de la création du groupe")
        else:
            st.warning("⚠ Veuillez entrer un nom de groupe")

st.markdown("---")

# Section Liste des groupes avec dataframe éditable
st.markdown("## 📋 Tous mes groupes")

if user_groups:
    # Préparer les données pour le dataframe
    groups_list = []
    for group_id, group_data in user_groups.items():
        groups_list.append({
            'ID': group_id,
            'Nom': group_data['name'],
            'Propriétaire': group_data['owner'],
            'Items': len(group_data.get('items', [])),
            'Partagé avec': ', '.join(group_data.get('shared_with', [])) if group_data.get('shared_with') else '',
            'Par défaut': '✓' if group_data.get('is_default', False) else '',
            'Créé le': group_data.get('created_at', 'N/A')[:10],
        })

    df_groups = pd.DataFrame(groups_list)

    # Afficher le dataframe
    st.dataframe(
        df_groups,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small", disabled=True),
            "Nom": st.column_config.TextColumn("Nom", width="medium"),
            "Propriétaire": st.column_config.TextColumn("Propriétaire", width="small"),
            "Items": st.column_config.NumberColumn("Items", width="small"),
            "Partagé avec": st.column_config.TextColumn("Partagé avec", width="medium"),
            "Par défaut": st.column_config.TextColumn("Défaut", width="small"),
            "Créé le": st.column_config.TextColumn("Créé le", width="small"),
        }
    )

    st.markdown("---")

    # Section pour modifier/supprimer un groupe
    st.markdown("## ✏️ Modifier ou Supprimer un groupe")

    # Sélectionner un groupe à modifier/supprimer
    editable_groups = {gid: gdata for gid, gdata in user_groups.items() if gdata['owner'] == CURRENT_USER}

    if editable_groups:
        selected_group_id = st.selectbox(
            "Sélectionner un groupe",
            options=list(editable_groups.keys()),
            format_func=lambda x: f"{editable_groups[x]['name']} {'(Par défaut)' if editable_groups[x].get('is_default', False) else ''}",
            key="selected_group_for_edit"
        )

        selected_group = editable_groups[selected_group_id]

        # Afficher les détails du groupe sélectionné
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"**Nom:** {selected_group['name']}")
            st.info(f"**Propriétaire:** {selected_group['owner']}")
        with col_info2:
            st.info(f"**Items:** {len(selected_group.get('items', []))}")
            st.info(f"**Créé le:** {selected_group.get('created_at', 'N/A')[:10]}")

        # Formulaire de modification
        with st.form(f"edit_form_{selected_group_id}"):
            st.markdown("### Modifier ce groupe")

            # Nom du groupe (non éditable si c'est un groupe par défaut)
            if selected_group.get('is_default', False):
                st.text_input("Nom du groupe", value=selected_group['name'], disabled=True, help="Les groupes par défaut ne peuvent pas être renommés")
                edit_name = selected_group['name']
            else:
                edit_name = st.text_input("Nom du groupe", value=selected_group['name'], key=f"edit_name_{selected_group_id}")

            # Liste des utilisateurs pour le partage
            edit_shared_users = st.multiselect(
                "Partager avec",
                options=all_users,
                default=selected_group.get('shared_with', []),
                key=f"edit_shared_{selected_group_id}",
                help="Sélectionnez les utilisateurs avec qui partager ce groupe"
            )

            col_save, col_delete = st.columns(2)

            with col_save:
                submit_edit = st.form_submit_button("💾 Sauvegarder les modifications", use_container_width=True)

            with col_delete:
                # Ne pas permettre la suppression des groupes par défaut
                if selected_group.get('is_default', False):
                    st.form_submit_button("🗑️ Supprimer (désactivé)", use_container_width=True, disabled=True)
                    submit_delete = False
                else:
                    submit_delete = st.form_submit_button("🗑️ Supprimer le groupe", use_container_width=True, type="secondary")

            if submit_edit:
                # Modifier le groupe
                groups_data = load_groups_data()
                if selected_group_id in groups_data['groups']:
                    groups_data['groups'][selected_group_id]['name'] = edit_name
                    groups_data['groups'][selected_group_id]['shared_with'] = edit_shared_users
                    if save_groups_data(groups_data):
                        # Invalider le cache
                        st.cache_data.clear()
                        st.success("✓ Groupe modifié avec succès")
                        st.rerun()
                    else:
                        st.error("✗ Erreur lors de la modification")

            if submit_delete:
                if delete_group(selected_group_id):
                    # Invalider le cache
                    st.cache_data.clear()
                    st.success("✓ Groupe supprimé avec succès")
                    st.rerun()
                else:
                    st.error("✗ Erreur lors de la suppression")

    else:
        st.info("Vous n'avez créé aucun groupe éditable. Le groupe 'favoris' est un groupe par défaut non supprimable.")

else:
    st.info("Aucun groupe trouvé. Créez votre premier groupe ci-dessus.")

import streamlit as st
import pandas as pd
from utils import (
    get_user_groups, create_group, delete_group, load_groups_data, save_groups_data
)
from config import CURRENT_USER

# Configuration
st.set_page_config(layout="wide")

st.markdown("# 👥 Gestion des Groupes")

# Afficher les toasts en attente
if 'toast_message' in st.session_state:
    st.toast(st.session_state.toast_message, icon=st.session_state.toast_icon)
    del st.session_state.toast_message
    del st.session_state.toast_icon

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

# Section Créer un nouveau groupe
st.markdown("### ➕ Créer un nouveau groupe")

with st.form("create_group_form"):
    new_group_name = st.text_input("Nom du groupe", key="form_new_group_name")

    submit_create = st.form_submit_button("Créer le groupe", use_container_width=True)

    if submit_create:
        if new_group_name:
            # Vérifier si un groupe avec ce nom existe déjà pour l'utilisateur
            existing_group_id = f"{CURRENT_USER}_{new_group_name}"
            groups_data = load_groups_data()

            if existing_group_id in groups_data.get('groups', {}):
                st.toast(f"⚠ Un groupe nommé '{new_group_name}' existe déjà", icon="⚠️")
            else:
                group_id = create_group(new_group_name, [])
                if group_id:
                    # Invalider le cache
                    st.cache_data.clear()
                    st.session_state.toast_message = f"✓ Groupe '{new_group_name}' créé avec succès"
                    st.session_state.toast_icon = "✅"
                    st.rerun()
                else:
                    st.toast("✗ Erreur lors de la création du groupe", icon="❌")
        else:
            st.toast("⚠ Veuillez entrer un nom de groupe", icon="⚠️")

if user_groups:
    # Récupérer la liste de tous les utilisateurs
    groups_data = load_groups_data()
    all_users = [u for u in groups_data.get('users', []) if u != CURRENT_USER]

    # Séparer les groupes en deux catégories : éditables et non éditables
    editable_groups_list = []
    readonly_groups_list = []

    for group_id, group_data in user_groups.items():
        row = {
            '☑️': False,  # Colonne de sélection
            'ID': group_id,
            'Nom': group_data['name'],
            'Propriétaire': group_data['owner'],
            'Items': len(group_data.get('items', [])),
            'Créé le': group_data.get('created_at', 'N/A')[:10],
        }

        # Ajouter une colonne booléenne pour chaque utilisateur
        shared_with = group_data.get('shared_with', [])
        for user in all_users:
            row[f'Partagé - {user}'] = user in shared_with

        # Séparer selon si c'est éditable ou non
        if group_data['owner'] == CURRENT_USER:
            editable_groups_list.append(row)
        else:
            # Pour les groupes en lecture seule, ajouter une colonne "Partagé avec"
            row['Partagé avec'] = ', '.join(group_data.get('shared_with', [])) if group_data.get('shared_with') else '-'
            readonly_groups_list.append(row)

    # Configuration des colonnes pour les groupes éditables
    column_config_editable = {
        "☑️": st.column_config.CheckboxColumn("☑️", width="small"),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Items": st.column_config.NumberColumn("Items", width="small", disabled=True),
        "Créé le": st.column_config.TextColumn("Créé le", width="small", disabled=True),
    }

    # Configuration des colonnes pour les groupes non éditables
    column_config_readonly = {
        "☑️": st.column_config.CheckboxColumn("☑️", width="small"),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Items": st.column_config.NumberColumn("Items", width="small"),
        "Créé le": st.column_config.TextColumn("Créé le", width="small"),
        "Propriétaire": st.column_config.TextColumn("Propriétaire", width="small"),
        "Partagé avec": st.column_config.TextColumn("Partagé avec", width="medium"),
    }

    # Ajouter la configuration pour les colonnes booléennes de partage (uniquement pour les groupes éditables)
    for user in all_users:
        column_config_editable[f'Partagé - {user}'] = st.column_config.CheckboxColumn(
            f'Partager avec {user}',
            help=f"Partager avec {user}",
            width="small"
        )

    # Afficher d'abord les groupes éditables
    if editable_groups_list:
        st.markdown("### ✏️ Mes groupes")

        df_editable = pd.DataFrame(editable_groups_list)

        with st.form("edit_groups_form"):
            # Sélectionner uniquement les colonnes à afficher (sans ID et Propriétaire)
            columns_editable = ['☑️', 'Nom', 'Items', 'Créé le'] + [f'Partagé - {user}' for user in all_users]
            df_editable_filtered = df_editable[columns_editable]

            edited_df = st.data_editor(
                df_editable_filtered,
                use_container_width=True,
                hide_index=True,
                column_config=column_config_editable,
                disabled=["Items", "Créé le"],
                num_rows="fixed",
                key="groups_editor"
            )

            # Boutons alignés à droite
            col_spacer, col_save, col_delete = st.columns([2, 1, 1])

            with col_save:
                submit_save = st.form_submit_button("✓ Sauvegarder", use_container_width=True, type="primary")

            with col_delete:
                submit_delete = st.form_submit_button("🗑️ Supprimer", use_container_width=True, type="secondary")

            if submit_save:
                # Parcourir les modifications
                success_count = 0
                error_count = 0

                for idx in range(len(df_editable_filtered)):
                    # Récupérer l'ID depuis le dataframe original
                    group_id = df_editable.iloc[idx]['ID']

                    # Vérifier si le nom a changé
                    old_name = df_editable_filtered.iloc[idx]['Nom']
                    new_name = edited_df.iloc[idx]['Nom']

                    # Vérifier les changements de partage
                    new_shared_with = []
                    for user in all_users:
                        col_name = f'Partagé - {user}'
                        if edited_df.iloc[idx][col_name]:
                            new_shared_with.append(user)

                    old_shared_with = []
                    for user in all_users:
                        col_name = f'Partagé - {user}'
                        if df_editable_filtered.iloc[idx][col_name]:
                            old_shared_with.append(user)

                    # Si des changements sont détectés
                    if old_name != new_name or set(old_shared_with) != set(new_shared_with):
                        groups_data = load_groups_data()
                        if group_id in groups_data['groups']:
                            groups_data['groups'][group_id]['name'] = new_name
                            groups_data['groups'][group_id]['shared_with'] = new_shared_with

                            if save_groups_data(groups_data):
                                success_count += 1
                            else:
                                error_count += 1

                # Invalider le cache
                st.cache_data.clear()

                if success_count > 0:
                    st.session_state.toast_message = f"✓ {success_count} groupe(s) modifié(s) avec succès"
                    st.session_state.toast_icon = "✅"
                    st.rerun()
                elif error_count > 0:
                    st.toast(f"✗ Erreur lors de la modification de {error_count} groupe(s)", icon="❌")

            if submit_delete:
                # Récupérer les groupes sélectionnés
                selected_groups = []
                for idx in range(len(edited_df)):
                    if edited_df.iloc[idx]['☑️']:
                        # Récupérer l'ID depuis le dataframe original
                        group_id = df_editable.iloc[idx]['ID']
                        group_name = edited_df.iloc[idx]['Nom']
                        # Vérifier qu'on en est propriétaire
                        group_data = user_groups.get(group_id)
                        if group_data and group_data['owner'] == CURRENT_USER:
                            selected_groups.append((group_id, group_name))

                if selected_groups:
                    # Supprimer les groupes sélectionnés
                    success_count = 0
                    for group_id, group_name in selected_groups:
                        if delete_group(group_id):
                            success_count += 1

                    st.cache_data.clear()
                    if success_count > 0:
                        st.session_state.toast_message = f"✓ {success_count} groupe(s) supprimé(s) avec succès"
                        st.session_state.toast_icon = "✅"
                        st.rerun()
                    else:
                        st.toast("⚠ Aucun élément supprimé", icon="⚠️")
                else:
                    st.toast("⚠ Aucun groupe sélectionné", icon="⚠️")

    # Afficher ensuite les groupes en lecture seule
    if readonly_groups_list:
        st.markdown("### 👁️ Partagés avec moi")

        df_readonly = pd.DataFrame(readonly_groups_list)

        # Sélectionner et réordonner les colonnes : sélection, Nom, Items, Créé le, Propriétaire, Partagé avec
        columns_to_display = ['☑️', 'Nom', 'Items', 'Créé le', 'Propriétaire', 'Partagé avec']
        df_readonly_filtered = df_readonly[columns_to_display]

        with st.form("readonly_groups_form"):
            edited_readonly_df = st.data_editor(
                df_readonly_filtered,
                use_container_width=True,
                hide_index=True,
                column_config=column_config_readonly,
                disabled=["Nom", "Items", "Créé le", "Propriétaire", "Partagé avec"],
                num_rows="fixed",
                key="readonly_groups_editor"
            )

            # Bouton aligné à droite
            col_spacer_leave, col_leave = st.columns([3, 1])

            with col_leave:
                submit_leave = st.form_submit_button("🚪 Quitter", use_container_width=True, type="secondary")

            if submit_leave:
                # Récupérer les groupes sélectionnés
                selected_groups = []
                for idx in range(len(edited_readonly_df)):
                    if edited_readonly_df.iloc[idx]['☑️']:
                        # Récupérer l'ID depuis le dataframe original
                        group_id = df_readonly.iloc[idx]['ID']
                        group_name = edited_readonly_df.iloc[idx]['Nom']
                        selected_groups.append((group_id, group_name))

                if selected_groups:
                    # Retirer l'utilisateur de la liste shared_with
                    success_count = 0
                    groups_data = load_groups_data()

                    for group_id, group_name in selected_groups:
                        if group_id in groups_data['groups']:
                            shared_with = groups_data['groups'][group_id].get('shared_with', [])
                            if CURRENT_USER in shared_with:
                                shared_with.remove(CURRENT_USER)
                                groups_data['groups'][group_id]['shared_with'] = shared_with
                                success_count += 1

                    if success_count > 0 and save_groups_data(groups_data):
                        st.cache_data.clear()
                        st.session_state.toast_message = f"✓ Vous avez quitté {success_count} groupe(s) avec succès"
                        st.session_state.toast_icon = "✅"
                        st.rerun()
                    elif success_count > 0:
                        st.toast("✗ Erreur lors de la mise à jour des groupes", icon="❌")
                    else:
                        st.toast("✗ Aucun groupe quitté", icon="⚠️")
                else:
                    st.toast("⚠ Aucun groupe sélectionné", icon="⚠️")

else:
    st.info("Aucun groupe trouvé. Créez votre premier groupe ci-dessus.")

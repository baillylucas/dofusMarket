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
    new_group_name = st.text_input("Nom du groupe", key="form_new_group_name")

    submit_create = st.form_submit_button("Créer le groupe", use_container_width=True)

    if submit_create:
        if new_group_name:
            group_id = create_group(new_group_name, [])
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
    # Récupérer la liste de tous les utilisateurs
    groups_data = load_groups_data()
    all_users = [u for u in groups_data.get('users', []) if u != CURRENT_USER]

    # Séparer les groupes en deux catégories : éditables et non éditables
    editable_groups_list = []
    readonly_groups_list = []

    for group_id, group_data in user_groups.items():
        row = {
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
        "ID": st.column_config.TextColumn("ID", width="small", disabled=True),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Items": st.column_config.NumberColumn("Items", width="small", disabled=True),
        "Créé le": st.column_config.TextColumn("Créé le", width="small", disabled=True),
    }

    # Configuration des colonnes pour les groupes non éditables
    column_config_readonly = {
        "ID": st.column_config.TextColumn("ID", width="small"),
        "Nom": st.column_config.TextColumn("Nom", width="medium"),
        "Propriétaire": st.column_config.TextColumn("Propriétaire", width="small"),
        "Items": st.column_config.NumberColumn("Items", width="small"),
        "Partagé avec": st.column_config.TextColumn("Partagé avec", width="medium"),
        "Créé le": st.column_config.TextColumn("Créé le", width="small"),
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
        st.info("💡 Vous pouvez éditer directement le nom et les partages de vos groupes ci-dessous.")

        df_editable = pd.DataFrame(editable_groups_list)

        with st.form("edit_groups_form"):
            # Sélectionner uniquement les colonnes à afficher (sans Propriétaire)
            columns_editable = ['ID', 'Nom', 'Items', 'Créé le'] + [f'Partagé - {user}' for user in all_users]
            df_editable_filtered = df_editable[columns_editable]

            edited_df = st.data_editor(
                df_editable_filtered,
                use_container_width=True,
                hide_index=True,
                column_config=column_config_editable,
                disabled=["ID", "Items", "Créé le"],
                num_rows="fixed",
                key="groups_editor"
            )

            col_save, col_cancel = st.columns([1, 1])

            with col_save:
                submit_save = st.form_submit_button("✓ Sauvegarder toutes les modifications", use_container_width=True, type="primary")

            with col_cancel:
                submit_cancel = st.form_submit_button("✗ Annuler les modifications", use_container_width=True)

            if submit_save:
                # Parcourir les modifications
                success_count = 0
                error_count = 0

                for idx in range(len(df_editable_filtered)):
                    group_id = df_editable_filtered.iloc[idx]['ID']

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
                    st.success(f"✓ {success_count} groupe(s) modifié(s) avec succès")
                    st.rerun()
                if error_count > 0:
                    st.error(f"✗ Erreur lors de la modification de {error_count} groupe(s)")

            if submit_cancel:
                st.rerun()

    # Afficher ensuite les groupes en lecture seule
    if readonly_groups_list:
        st.markdown("---")
        st.markdown("### 👁️ Partagés avec moi")
        st.info("🔒 Ces groupes ne peuvent pas être modifiés car ils appartiennent à d'autres utilisateurs.")

        df_readonly = pd.DataFrame(readonly_groups_list)

        # Sélectionner uniquement les colonnes sans les colonnes booléennes
        columns_to_display = ['ID', 'Nom', 'Propriétaire', 'Items', 'Partagé avec', 'Créé le']
        df_readonly_filtered = df_readonly[columns_to_display]

        st.dataframe(
            df_readonly_filtered,
            use_container_width=True,
            hide_index=True,
            column_config=column_config_readonly
        )

    st.markdown("---")

    # Section pour supprimer un groupe
    st.markdown("## 🗑️ Supprimer un groupe")

    # Sélectionner un groupe à supprimer (uniquement les groupes éditables non par défaut)
    deletable_groups = {
        gid: gdata for gid, gdata in user_groups.items()
        if gdata['owner'] == CURRENT_USER and not gdata.get('is_default', False)
    }

    if deletable_groups:
        selected_group_id = st.selectbox(
            "Sélectionner un groupe à supprimer",
            options=list(deletable_groups.keys()),
            format_func=lambda x: deletable_groups[x]['name'],
            key="selected_group_for_delete"
        )

        selected_group = deletable_groups[selected_group_id]

        st.warning(f"⚠️ Vous êtes sur le point de supprimer le groupe **{selected_group['name']}** qui contient **{len(selected_group.get('items', []))}** item(s).")

        if st.button("🗑️ Confirmer la suppression", use_container_width=True, type="secondary"):
            if delete_group(selected_group_id):
                # Invalider le cache
                st.cache_data.clear()
                st.success("✓ Groupe supprimé avec succès")
                st.rerun()
            else:
                st.error("✗ Erreur lors de la suppression")
    else:
        st.info("Vous n'avez aucun groupe supprimable. Les groupes par défaut ne peuvent pas être supprimés.")

else:
    st.info("Aucun groupe trouvé. Créez votre premier groupe ci-dessus.")

import streamlit as st
import pandas as pd

df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Nom': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Score': [85, 90, 75]
})

# Filtrer pour ne garder que la ligne d'Alice
df_alice = df[df['Nom'] == 'Alice'].copy()

# Désactiver la colonne ID
edited_df = st.data_editor(
    df_alice,
    disabled=['ID']
)

# Si vous avez besoin de l'index original
# df_alice = df[df['Nom'] == 'Alice'].copy()
# edited_df = st.data_editor(df_alice, disabled=['ID'])
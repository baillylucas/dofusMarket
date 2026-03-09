import streamlit as st

# Define the pages
page_prices = st.Page("pages/prices.py", title="Prix des items", icon="📊")
page_groups = st.Page("pages/groups.py", title="Gestion des groupes", icon="👥")
page_scrapper = st.Page("pages/scrapper.py", title="Scrapper", icon="🔍")
page_achat_revente = st.Page("pages/achat_revente.py", title="Achat/Revente", icon="🔍")
page_test = st.Page("pages/test.py", title="Test", icon="🔍")
page_familier = st.Page("pages/familier.py", title="Familiers", icon="🔍")
page_bashing = st.Page("pages/bashing.py", title="Bashing", icon="🔍")
# page_test_onglet = st.Page("pages/test_onglets.py", title="Test onglets", icon="🔍")


# Set up navigation
# pg = st.navigation([page_prices, page_groups, page_scrapper, page_test])
pg = st.navigation([page_prices, page_groups, page_scrapper, page_achat_revente, page_familier, page_bashing])

# Initialize scrapper list in session state if not present
if 'scrapper_items' not in st.session_state:
    st.session_state.scrapper_items = []

# Run the selected page
pg.run()
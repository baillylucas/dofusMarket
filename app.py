import streamlit as st

# Define the pages
page_1 = st.Page("page1.py", title="Main Page", icon="🎈")
page_2 = st.Page("page2.py", title="Page 2", icon="❄️")
page_3 = st.Page("page3.py", title="Page 3", icon="🎉")

# Set up navigation
pg = st.navigation([page_1, page_2, page_3])

# Run the selected page
pg.run()
import streamlit as st

# Define your individual pages
sweepstake_page = st.Page(
    "sweepstake.py", 
    title="Draw & Entries"
)
live_updates_page = st.Page(
    "live_updates.py", 
    title="World Cup Live Center", 
)

# Initialize modern top navigation navigation frame
pg = st.navigation(
    {"Menu": [sweepstake_page, live_updates_page]}, 
    position="top"
)

# Run the selected page
pg.run()
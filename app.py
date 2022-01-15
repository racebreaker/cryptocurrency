# app.py
import app8
import notes

import streamlit as st
PAGES = {
    "Cryptocurrency": app8,
    "Release Notes": notes,
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

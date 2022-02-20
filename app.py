# app.py
import app1
import app8
import app9
import app5
import notes

import streamlit as st
PAGES = {
    "Algorithmic Trading": app8,
    "Company Valuation (DCF)": app9,
    "Microeconomics Data": app5,
    "Release Notes": notes,
}
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

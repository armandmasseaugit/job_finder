import streamlit as st
from st_on_hover_tabs import on_hover_tabs

from web_app.frontend.pages_ import explore_offers, home

st.set_page_config(page_title="Job Finder", layout="wide")


# Importing stylesheet
st.markdown(
    "<style>" + open("web_app/frontend/style.css").read() + "</style>",
    unsafe_allow_html=True,
)

with st.sidebar:
    tabs = on_hover_tabs(
        tabName=["Home", "Explore Offers"],
        iconName=["home", "explore offers"],
        styles={
            "navtab": {
                "background-color": "#111",
                "color": "#818181",
                "font-size": "18px",
                "transition": ".3s",
                "white-space": "nowrap",
                "text-transform": "uppercase",
            },
            "tabOptionsStyle": {":hover :hover": {"color": "red", "cursor": "pointer"}},
            "iconStyle": {"position": "fixed", "left": "7.5px", "text-align": "left"},
            "tabStyle": {
                "list-style-type": "none",
                "margin-bottom": "30px",
                "padding-left": "30px",
            },
        },
        key="1",
    )

if tabs == "Home":
    home.run()

if tabs == "Explore Offers":
    explore_offers.run()

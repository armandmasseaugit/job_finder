import requests
import streamlit as st
from streamlit_lottie import st_lottie

from web_app.frontend.utils.api_client import get_offers


def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def run():
    offers = get_offers()
    lottie_url = (
        "https://lottie.host/653a1188-a13c-4548-96ee-eee1f66e0023/3BFOn9nV58.json"
    )
    lottie_json = load_lottie_url(lottie_url)

    st.title("Job Finder")
    col1, col2 = st.columns([1, 2])
    with col1:
        st_lottie(lottie_json, height=250, key="robot")
    with col2:
        st.markdown(
            f"""
        ## 👋 Hi, I'm JobBot!
        I'm here to help you find your dream job.
        👉 Click on *Explore Offers* on the left to start applying!

        You have <span style='color:#007bff;font-weight:bold;'>{len(offers)}</span> new offers to check out.
        """,
            unsafe_allow_html=True,
        )

import streamlit as st
import pandas as pd
from PIL import Image
import requests
import json
import boto3
from io import BytesIO
from streamlit_lottie import st_lottie

from kedro.framework.startup import bootstrap_project
from kedro.framework.session import KedroSession
import os

# Bootstrap the Kedro project
project_path = os.getcwd()
bootstrap_project(project_path)

# Open a Kedro session
with KedroSession.create(project_path) as session:
    context = session.load_context()
    df = context.catalog.load("wttj_jobs_output")

df.sort_values(by="publication_date", ascending=False, inplace=True)
# --------- Multi-page navigation ----------
st.set_page_config(page_title="Job Finder", layout="wide")

from st_on_hover_tabs import on_hover_tabs

# Importing stylesheet
st.markdown(
    "<style>" + open("./streamlit_app/style.css").read() + "</style>",
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


def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Animation d’un robot assistant
lottie_url = "https://lottie.host/653a1188-a13c-4548-96ee-eee1f66e0023/3BFOn9nV58.json"
lottie_json = load_lottie_url(lottie_url)

if tabs == "Home":
    st.title("Job Finder")

    col1, col2 = st.columns([1, 2])
    with col1:
        st_lottie(lottie_json, height=250, key="robot")
    with col2:
        st.markdown(
            """
        ## 👋 Hi, I'm JobBot!  
        I'm here to help you find your dream job.  
        👉 Click on *Explore Offers* on the left to start applying!

        You have <span style='color:#007bff;font-weight:bold;'>{}</span> new offers to check out.
        """.format(
                df.shape[0]
            ),
            unsafe_allow_html=True,
        )

# --------- Explore offers page ----------

# --- Configurer le client S3 ---
s3 = boto3.client(
    "s3",
    aws_access_key_id="AKIAT2BOKVQCSHQRHA4O",
    aws_secret_access_key="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",
    region_name="us-east-1",
)

BUCKET = "wttj-scraping"
KEY_LIKES = "job_likes.json"


@st.cache_data(ttl=300)
def load_likes_from_s3() -> dict:
    """
    Lit le fichier JSON 'job_likes.json' depuis S3.
    Retourne un dict { job_reference: "like"|"dislike" }.
    Si le fichier n'existe pas, renvoie {}.
    """
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=KEY_LIKES)
        data = obj["Body"].read().decode("utf-8")
        return json.loads(data)
    except s3.exceptions.NoSuchKey:
        return {}
    except Exception:
        return {}


def update_like_in_s3(job_ref: str, feedback: str):
    """
    Met à jour un seul feedback dans le fichier JSON S3, sans écraser les autres.
    - job_ref: l'identifiant unique de l'offre
    - feedback: 'like' ou 'dislike'
    """
    try:
        # Lire l’existant
        obj = s3.get_object(Bucket=BUCKET, Key=KEY_LIKES)
        existing_data = json.loads(obj["Body"].read().decode("utf-8"))
    except s3.exceptions.NoSuchKey:
        existing_data = {}
    except Exception as e:
        st.error(f"Erreur lecture S3: {e}")
        return

    # Mettre à jour la valeur pour ce job
    existing_data[job_ref] = feedback

    # Réécriture dans S3
    try:
        s3.put_object(
            Bucket=BUCKET,
            Key=KEY_LIKES,
            Body=json.dumps(existing_data, indent=2),
            ContentType="application/json",
        )
    except Exception as e:
        st.error(f"Erreur écriture S3: {e}")


# Charge les likes en mémoire
likes_dict = load_likes_from_s3()

# … passer à la partie navigation et affichage
if tabs == "Explore Offers":
    st.title("🔍 Available Offers")

    # --- Filtre par date ---
    min_date = pd.to_datetime(df["publication_date"]).min().date()
    max_date = pd.to_datetime(df["publication_date"]).max().date()
    selected_date = st.date_input(
        "Show offers published on or after:",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )

    df["publication_date"] = pd.to_datetime(df["publication_date"])
    filtered_df = df[df["publication_date"].dt.date >= selected_date]

    st.write(
        f"Displaying {filtered_df.shape[0]} offers published since {selected_date}:"
    )

    recent_threshold = pd.Timestamp.now() - pd.Timedelta(days=3)

    for idx, row in filtered_df.iterrows():
        ref = row["reference"]
        is_recent = row["publication_date"] >= recent_threshold

        # Vérifie si déjà liké/disliké
        liked = likes_dict.get(ref) == "like"
        disliked = likes_dict.get(ref) == "dislike"

        with st.container():
            cols = st.columns([1, 5])
            with cols[0]:
                st.image(row["logo_url"], width=80)
            with cols[1]:
                if is_recent:
                    st.markdown(
                        f'<h3><a href="{row["url"]}">{row["name"]}</a> '
                        f'<span style="color:red;">🔴 NEW!</span></h3>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<h3><a href="{row["url"]}">{row["name"]}</a></h3>',
                        unsafe_allow_html=True,
                    )

                st.markdown(f"**Company:** {row['company_name']}")
                st.markdown(f"🗓️ Published on: {row['publication_date'].date()}")
                st.markdown(f"🔁 Remote: `{row['remote']}`")
                st.markdown(f"🌐 Website: `{row['provider']}`")
                st.markdown(
                    f"Reference: `{row['reference']}`"
                )  # TODO: enlever la reference

                # --- Boutons dynamiques ---
                col_like, col_dislike = st.columns([1, 1])
                like_key = f"{ref}_like"
                dislike_key = f"{ref}_dislike"
                # TODO: see if it is possible to dynamically rerun (buttons)
                with col_like:
                    if liked:
                        st.button("❤️", key=f"{like_key}_disabled", disabled=True)
                    else:
                        if st.button("🤍 Like", key=like_key):
                            likes_dict[ref] = "like"
                            update_like_in_s3(ref, "like")
                            if like_key in st.session_state:
                                del st.session_state[like_key]
                            st.rerun()

                with col_dislike:
                    if disliked:
                        st.button("🚫", key=f"{dislike_key}_disabled", disabled=True)
                    else:
                        if st.button("👎 Dislike", key=dislike_key):
                            likes_dict[ref] = "dislike"
                            update_like_in_s3(ref, "dislike")
                            if dislike_key in st.session_state:
                                del st.session_state[dislike_key]
                            st.rerun()

        st.markdown("---")

    st.markdown("End of list")

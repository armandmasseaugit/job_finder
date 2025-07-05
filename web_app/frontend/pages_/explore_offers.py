import streamlit as st
import pandas as pd
from web_app.frontend.utils.api_client import (
    get_offers,
    get_likes,
    get_relevance,
    post_like,
)


def run():
    st.title("🔍 Available Offers")

    offers = pd.DataFrame(get_offers())
    likes_dict = get_likes()
    relevance_dict = get_relevance()

    offers["publication_date"] = pd.to_datetime(offers["publication_date"])
    min_date = offers["publication_date"].min().date()
    max_date = offers["publication_date"].max().date()

    selected_date = st.date_input(
        "Show offers published on or after:",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )

    filtered_df = offers[offers["publication_date"].dt.date >= selected_date]

    sort_option = st.selectbox(
        "Sort offers by:",
        options=["Publication date (newest first)", "Relevance score (high to low)"],
    )

    if sort_option == "Relevance score (high to low)":
        filtered_df["relevance"] = filtered_df["reference"].map(
            lambda ref: relevance_dict.get(ref, 0)
        )
        filtered_df = filtered_df.sort_values(by="relevance", ascending=False)
    else:
        filtered_df = filtered_df.sort_values(by="publication_date", ascending=False)

    st.write(
        f"Displaying {filtered_df.shape[0]} offers published since {selected_date}:"
    )

    recent_threshold = pd.Timestamp.now() - pd.Timedelta(days=3)

    for _, row in filtered_df.iterrows():
        ref = row["reference"]
        is_recent = row["publication_date"] >= recent_threshold
        liked = likes_dict.get(ref) == "like"
        disliked = likes_dict.get(ref) == "dislike"

        with st.container():
            cols = st.columns([1, 5])
            with cols[0]:
                st.image(row["logo_url"], width=80)
            with cols[1]:
                title = f'<h3><a href="{row["url"]}">{row["name"]}</a>'
                if is_recent:
                    title += ' <span style="color:red;">🔴 NEW!</span>'
                title += "</h3>"
                st.markdown(title, unsafe_allow_html=True)

                st.markdown(f"**Company:** {row['company_name']}")
                st.markdown(f"🗓️ Published on: {row['publication_date'].date()}")
                st.markdown(f"🔁 Remote: `{row['remote']}`")
                st.markdown(f"🌐 Website: `{row['provider']}`")
                st.markdown(
                    f"Reference: `{row['reference']}`"
                )  # TODO: peut être retiré

                # Affichage du score de pertinence si disponible
                relevance_score = relevance_dict.get(ref)
                if relevance_score is not None:
                    st.markdown(f"**Relevance score:** {relevance_score:.3f}")

                col_like, col_dislike = st.columns([1, 1])
                like_key = f"{ref}_like"
                dislike_key = f"{ref}_dislike"

                with col_like:
                    if liked:
                        st.button("❤️", key=f"{like_key}_disabled", disabled=True)
                    else:
                        if st.button("🤍 Like", key=like_key):
                            likes_dict[ref] = "like"
                            post_like(ref, "like")
                            if like_key in st.session_state:
                                del st.session_state[like_key]
                            st.rerun()

                with col_dislike:
                    if disliked:
                        st.button("🚫", key=f"{dislike_key}_disabled", disabled=True)
                    else:
                        if st.button("👎 Dislike", key=dislike_key):
                            likes_dict[ref] = "dislike"
                            post_like(ref, "dislike")
                            if dislike_key in st.session_state:
                                del st.session_state[dislike_key]
                            st.rerun()
        st.markdown("---")

    st.markdown("End of list")
